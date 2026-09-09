"""
Copy guard: Reject instruction leaks, bare labels, and prompt artifacts
so they never land on presentation slides.
Ported and adapted from quick-slide-be for PersuAId slide deck engine.
"""

from __future__ import annotations

import re

# Phrases stamped as writer jobs or prompt instructions.
# If an LLM pastes them, strip them out.
_META_NEEDLES = (
    "campaign facts",
    "from brief list",
    "do not copy",
    "template sample",
    "max 6 words",
    "short phrase",
    "not template",
    "slot_hints",
    "min_chars",
    "max_chars",
    "write for this",
    "this slide only",
    "replace sample",
    "replace leftover",
    "do not invent",
    "do not rewrite",
    "do not paste",
    "honor each",
    "honor per-slot",
    "unlocked slots",
    "pillar name",
    "takeout and action",
    "named competitor",
    "competitor name",
    "takeout for this",
    "real name, never",
    "one learning line",
    "learning line then one action",
    "buzz, sentiment, or engagement",
    "short label, not a paragraph",
    "section title for",
    "deck brief (sample)",
    "**client:**",
    "**campaign:**",
    "**finding:**",
    "**action:**",
)

_SLIDE_N_PREFIX_RE = re.compile(r"^slide\s+\d+[\s:—–-]+", re.I)
_MD_BOLD_RE = re.compile(r"\*{1,3}([^*]+)\*{1,3}")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^\)]+\)")
_PLACEHOLDER_RE = re.compile(
    r"^(competitor name(?:\s+\d+)?|sample (?:headline|kicker|body|name)|placeholder|insight)$",
    re.I,
)


def is_meta_copy(text: str) -> bool:
    """True if the text looks like an unstripped writer instruction or placeholder."""
    norm = (text or "").strip().lower()
    if not norm:
        return False
    if _PLACEHOLDER_RE.match(norm):
        return True
    return any(needle in norm for needle in _META_NEEDLES)


def sanitize_generated_copy(text: str) -> str:
    """
    Cleans generated text for presentation slides:
    - Strips markdown asterisks (**bold** -> bold)
    - Strips markdown links ([text](url) -> text)
    - Strips 'Slide N — ' prefixes
    - Strips prompt meta phrases
    """
    out = (text or "").strip()
    if not out:
        return ""

    # Strip markdown bold/italic
    out = _MD_BOLD_RE.sub(r"\1", out)
    # Strip markdown links
    out = _MD_LINK_RE.sub(r"\1", out)
    # Strip Slide N prefix
    out = _SLIDE_N_PREFIX_RE.sub("", out).strip()

    # Strip known meta instruction lines if isolated
    for needle in _META_NEEDLES:
        pattern = re.compile(re.escape(needle), re.I)
        out = pattern.sub("", out)

    # Clean up double spaces resulting from removals
    out = re.sub(r"[ \t]+", " ", out).strip()
    return out
