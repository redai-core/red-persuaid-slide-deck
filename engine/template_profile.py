#!/usr/bin/env python3
"""
PersuAId Template Profile Specification
Defines the schema for normalized PPTX templates, unit-space geometry,
color palettes, typography hierarchy, recurring chrome, and semantic slot contracts.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class CanvasSpec:
    width_inches: float = 20.0
    height_inches: float = 11.25
    aspect_ratio: str = "16:9"
    content_x: float = 0.055   # 1.1" / 20.0"
    content_y: float = 0.213   # 2.4" / 11.25"
    content_w: float = 0.890   # 17.8" / 20.0"
    content_h: float = 0.684   # 7.7" / 11.25"


@dataclass
class PaletteTokens:
    background: str = "000000"          # Obsidian Black
    container_primary: str = "031E45"   # Midnight Navy
    container_secondary: str = "0D1117" # Dark Slate
    border_stroke: str = "1A2F4A"       # Subtle Navy Border
    accent_primary: str = "3EC0C0"      # Electric Cyan
    accent_secondary: str = "38A6A6"    # Deep Teal
    text_primary: str = "FFFFFF"        # Pure White
    text_secondary: str = "E8EEF4"      # Soft Gray
    text_muted: str = "8BA8C8"          # Slate Muted
    text_dark: str = "031E45"           # Dark text on bright accent callouts


@dataclass
class TypographyScale:
    font_title: str = "Arial"
    font_body: str = "Arial"
    size_hero_stat: int = 64
    size_cover_title: int = 56
    size_section_title: int = 48
    size_action_headline: int = 28
    size_card_header: int = 18
    size_body: int = 15
    size_kicker: int = 13
    size_micro: int = 11


@dataclass
class ChromeSpec:
    has_kicker_tag: bool = True
    has_header_divider: bool = False
    has_footer_disclaimer: bool = True
    has_brand_mark: bool = True
    disclaimer_text: str = "Confidential | Redcomm Strategy & Executive Advisory"
    footer_y: float = 0.924  # 10.4" / 11.25"


@dataclass
class ElementGeometry:
    """Normalized bounding box coordinates in unit space [0.0, 1.0]."""
    x: float
    y: float
    w: float
    h: float
    shape_type: str = "rectangle"  # rectangle, rounded_rectangle, text_box, media_placeholder
    fill_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width_pt: float = 1.0


@dataclass
class SlotContract:
    """A semantic content slot with character constraints to prevent container overflow."""
    slot_id: str
    role: str                       # kicker, action_headline, hero_metric, takeaway_banner, card_title, card_body, stat_label
    max_chars: int = 120
    recommended_chars: int = 80
    font_size: int = 15
    is_required: bool = True
    description: str = ""


@dataclass
class ArchetypeSpec:
    """Defines a recurring slide layout archetype within a template."""
    archetype_id: str               # e.g. ARCH-COVER, ARCH-HERO-STAT, ARCH-GAP-BAR
    name: str                       # e.g. "4-Column Metric Hero Grid"
    description: str
    suggested_acts: List[str] = field(default_factory=list) # ["Act I", "Act II"]
    background_color: Optional[str] = None
    elements: List[ElementGeometry] = field(default_factory=list)
    slots: List[SlotContract] = field(default_factory=list)

    def get_slot(self, slot_id: str) -> Optional[SlotContract]:
        for s in self.slots:
            if s.slot_id == slot_id:
                return s
        return None


@dataclass
class TemplateProfile:
    """Master template manifest containing all design tokens, geometry, and archetypes."""
    template_id: str
    name: str
    version: str = "1.0.0"
    source_file: Optional[str] = None
    canvas: CanvasSpec = field(default_factory=CanvasSpec)
    palette: PaletteTokens = field(default_factory=PaletteTokens)
    typography: TypographyScale = field(default_factory=TypographyScale)
    chrome: ChromeSpec = field(default_factory=ChromeSpec)
    archetypes: Dict[str, ArchetypeSpec] = field(default_factory=dict)

    def get_archetype_menu(self) -> List[Dict[str, Any]]:
        """Returns a compact ~300-token summary of available archetypes for the AI agent."""
        menu = []
        for arch_id, arch in self.archetypes.items():
            menu.append({
                "archetype_id": arch.archetype_id,
                "name": arch.name,
                "description": arch.description,
                "suggested_acts": arch.suggested_acts,
                "slot_keys": [s.slot_id for s in arch.slots],
            })
        return menu

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateProfile":
        canvas = CanvasSpec(**data.get("canvas", {}))
        palette = PaletteTokens(**data.get("palette", {}))
        typography = TypographyScale(**data.get("typography", {}))
        chrome = ChromeSpec(**data.get("chrome", {}))
        archetypes = {}
        for k, v in data.get("archetypes", {}).items():
            elements = [ElementGeometry(**el) for el in v.get("elements", [])]
            slots = [SlotContract(**sl) for sl in v.get("slots", [])]
            archetypes[k] = ArchetypeSpec(
                archetype_id=v.get("archetype_id", k),
                name=v.get("name", k),
                description=v.get("description", ""),
                suggested_acts=v.get("suggested_acts", []),
                background_color=v.get("background_color"),
                elements=elements,
                slots=slots,
            )
        return cls(
            template_id=data.get("template_id", "default"),
            name=data.get("name", "Default"),
            version=data.get("version", "1.0.0"),
            source_file=data.get("source_file"),
            canvas=canvas,
            palette=palette,
            typography=typography,
            chrome=chrome,
            archetypes=archetypes,
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "TemplateProfile":
        return cls.from_dict(json.loads(json_str))
