#!/usr/bin/env python3
"""
PersuAId Interactive Presentation Staging Manager
Tracks turn-based Act-by-Act presentation staging in ~/.persuaid/sessions/,
validates physical character budgets against template archetypes,
and coordinates compilation into native PPTX.
"""

import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.template_profile import TemplateProfile, ArchetypeSpec, SlotContract
from engine.template_decompiler import decompile_pptx_file
from engine.copy_guard import sanitize_generated_copy
from engine.copy_repair import finish_claim
from engine.text_budget import trim_to_char_budget

logger = logging.getLogger("staging-manager")

SESSIONS_DIR = Path.home() / ".persuaid" / "sessions"
DEFAULT_TEMPLATE_PATH = PROJECT_ROOT / "engine" / "templates" / "redcomm_master.json"


@dataclass
class StagedSlide:
    slide_number: int
    archetype_id: str
    act: str
    slots: Dict[str, Any] = field(default_factory=dict)
    notes: Optional[str] = None


@dataclass
class StagingValidationIssue:
    slide_number: int
    archetype_id: str
    slot_id: str
    issue_type: str  # "overflow", "missing_required", "unknown_slot"
    message: str
    current_length: int = 0
    max_length: int = 0


class DeckStagingManager:
    """Manages active deck staging sessions and character budget validation."""

    def __init__(self, sessions_dir: Optional[Path] = None):
        self.sessions_dir = sessions_dir or SESSIONS_DIR
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._template_cache: Dict[str, TemplateProfile] = {}

    def get_template(self, template_id_or_path: str) -> TemplateProfile:
        """Resolves a template profile from memory, template directory, or custom file."""
        if template_id_or_path in self._template_cache:
            return self._template_cache[template_id_or_path]

        p = Path(template_id_or_path)
        if p.exists():
            if p.suffix.lower() == ".json":
                profile = TemplateProfile.from_json(p.read_text(encoding="utf-8"))
            elif p.suffix.lower() in [".pptx", ".ppt"]:
                profile = decompile_pptx_file(str(p))
            else:
                raise ValueError(f"Unsupported template format: {p}")
            self._template_cache[profile.template_id] = profile
            return profile

        # Check default template
        if DEFAULT_TEMPLATE_PATH.exists():
            profile = TemplateProfile.from_json(DEFAULT_TEMPLATE_PATH.read_text(encoding="utf-8"))
            self._template_cache[profile.template_id] = profile
            return profile

        # Fallback to in-memory default profile
        profile = TemplateProfile(template_id="default", name="Default Redcomm Executive")
        return profile

    def create_session(
        self,
        brand: str,
        category: str,
        template_id_or_path: Optional[str] = None,
        competitors: str = "Competitor A, Competitor B",
        domain: Optional[str] = None,
        total_slides: int = 21,
    ) -> Dict[str, Any]:
        """Creates and stores a fresh staging session."""
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        template = self.get_template(template_id_or_path or "default")

        session_data = {
            "session_id": session_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "brand": brand,
            "category": category,
            "competitors": competitors,
            "domain": domain,
            "total_slides": total_slides,
            "template_id": template.template_id,
            "template_source": template.source_file,
            "acts_staged": {},
            "slides": {},
            "status": "in_progress",
        }

        self._save_session(session_id, session_data)

        return {
            "session_id": session_id,
            "brand": brand,
            "category": category,
            "template_id": template.template_id,
            "total_slides": total_slides,
            "archetype_menu": template.get_archetype_menu(),
            "message": f"Initialized presentation staging session '{session_id}' for {brand}. Next step: query persuaid_get_archetypes(session_id='{session_id}', act='Act I') and stage Act I slides.",
        }

    def get_archetypes_for_act(self, session_id: str, act: str) -> Dict[str, Any]:
        """Returns lightweight archetype micro-schemas relevant to a specific consulting act (~200 tokens)."""
        session = self._load_session(session_id)
        template = self.get_template(session.get("template_source") or session.get("template_id", "default"))

        act_clean = act.strip()
        relevant = {}
        for arch_id, arch in template.archetypes.items():
            if not arch.suggested_acts or any(act_clean.lower() in sa.lower() for sa in arch.suggested_acts):
                relevant[arch_id] = {
                    "name": arch.name,
                    "description": arch.description,
                    "slots": [
                        {
                            "slot_id": s.slot_id,
                            "role": s.role,
                            "max_chars": s.max_chars,
                            "recommended_chars": s.recommended_chars,
                            "description": s.description or s.role,
                        }
                        for s in arch.slots
                    ],
                }

        return {
            "session_id": session_id,
            "act": act,
            "archetypes": relevant,
        }

    def stage_act(
        self,
        session_id: str,
        act: str,
        slides: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Stages an entire Act (typically 3–5 slides) and performs immediate character budget validation.
        Catches container overflows on this single turn.
        """
        session = self._load_session(session_id)
        template = self.get_template(session.get("template_source") or session.get("template_id", "default"))

        issues: List[Dict[str, Any]] = []
        staged_count = 0

        for slide_data in slides:
            slide_no = slide_data.get("slide_number", len(session["slides"]) + 1)
            arch_id = slide_data.get("archetype_id", "ARCH-HERO-STAT")
            slots = slide_data.get("slots", {})

            arch = template.archetypes.get(arch_id)
            if not arch:
                issues.append({
                    "slide_number": slide_no,
                    "archetype_id": arch_id,
                    "slot_id": "",
                    "issue_type": "unknown_archetype",
                    "message": f"Archetype '{arch_id}' is not defined in template '{template.template_id}'. Available: {list(template.archetypes.keys())}",
                })
                continue

            # Character Budget & Slot Contract Validation with Deterministic Sanitization
            cleaned_slots: Dict[str, Any] = {}
            for slot_id, content in slots.items():
                slot_contract = arch.get_slot(slot_id)
                if isinstance(content, str):
                    # Clean markdown formatting and trailing dangling clauses
                    cleaned = finish_claim(sanitize_generated_copy(content))

                    if slot_contract:
                        cur_len = len(cleaned.strip())
                        if cur_len > slot_contract.max_chars:
                            # Flag overflow so validator warns the caller
                            issues.append({
                                "slide_number": slide_no,
                                "archetype_id": arch_id,
                                "slot_id": slot_id,
                                "issue_type": "overflow",
                                "message": f"Slot '{slot_id}' exceeds maximum character budget ({cur_len} chars > {slot_contract.max_chars} max). Please condense.",
                                "current_length": cur_len,
                                "max_length": slot_contract.max_chars,
                            })
                            # Trim for safe display in case the user proceeds anyway
                            cleaned = trim_to_char_budget(cleaned, slot_contract.max_chars)
                    cleaned_slots[slot_id] = cleaned
                else:
                    cleaned_slots[slot_id] = content

            session["slides"][str(slide_no)] = {
                "slide_number": slide_no,
                "archetype_id": arch_id,
                "act": act,
                "slots": cleaned_slots,
                "notes": slide_data.get("notes"),
            }
            staged_count += 1

        session["acts_staged"][act] = {
            "slide_count": staged_count,
            "staged_at": time.time(),
        }
        session["updated_at"] = time.time()
        self._save_session(session_id, session)

        has_blocking = any(i["issue_type"] == "overflow" for i in issues)

        return {
            "session_id": session_id,
            "act": act,
            "staged_slides": staged_count,
            "total_staged_so_far": len(session["slides"]),
            "target_slides": session["total_slides"],
            "validation_passed": not has_blocking,
            "issues": issues,
            "message": (
                f"Successfully staged {staged_count} slides for {act} (Total: {len(session['slides'])}/{session['total_slides']})."
                if not issues
                else f"Staged with {len(issues)} character/slot warnings. Please review issues."
            ),
        }

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieves raw session data."""
        return self._load_session(session_id)

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Retrieves session progress and staged slide count."""
        session = self._load_session(session_id)
        return {
            "session_id": session_id,
            "brand": session["brand"],
            "category": session["category"],
            "template_id": session["template_id"],
            "total_slides": session["total_slides"],
            "staged_slide_count": len(session["slides"]),
            "acts_staged": list(session["acts_staged"].keys()),
            "status": session["status"],
        }

    def _save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        p = self.sessions_dir / f"{session_id}.json"
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_session(self, session_id: str) -> Dict[str, Any]:
        p = self.sessions_dir / f"{session_id}.json"
        if not p.exists():
            raise FileNotFoundError(f"Staging session not found: {session_id}")
        return json.loads(p.read_text(encoding="utf-8"))
