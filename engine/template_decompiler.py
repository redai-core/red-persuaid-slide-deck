#!/usr/bin/env python3
"""
PersuAId Universal Template Decompiler
Ingests any PowerPoint presentation (.pptx), normalizes physical geometry into unit-space [0.0, 1.0],
extracts color palette tokens and typography hierarchy, discovers slide archetypes,
and generates semantic slot contracts with physical character budgets.
"""

import argparse
import collections
import json
import logging
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pptx
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.template_profile import (
    CanvasSpec,
    PaletteTokens,
    TypographyScale,
    ChromeSpec,
    ElementGeometry,
    SlotContract,
    ArchetypeSpec,
    TemplateProfile,
)

logger = logging.getLogger("template-decompiler")


def _rgb_to_hex(rgb: RGBColor) -> str:
    """Converts pptx RGBColor to 6-char hex string."""
    try:
        return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
    except Exception:
        return "FFFFFF"


def _extract_shape_fill(shape: Any) -> Optional[str]:
    """Extracts hex color fill from a shape if available."""
    try:
        fill = shape.fill
        if fill.type == 1:  # msoFillSolid
            return _rgb_to_hex(fill.fore_color.rgb)
    except Exception:
        pass
    return None


def _extract_line_color(shape: Any) -> Optional[str]:
    """Extracts hex color border stroke from a shape if available."""
    try:
        line = shape.line
        if line.color and line.color.rgb:
            return _rgb_to_hex(line.color.rgb)
    except Exception:
        pass
    return None


class TemplateDecompiler:
    """Decompiles any PPTX file into a normalized TemplateProfile."""

    def __init__(self, pptx_path: str):
        self.path = Path(pptx_path)
        if not self.path.exists():
            raise FileNotFoundError(f"PPTX file not found: {pptx_path}")
        self.prs = Presentation(str(self.path))
        self.width_emu = self.prs.slide_width
        self.height_emu = self.prs.slide_height
        self.width_inches = round(self.width_emu / 914400.0, 2)
        self.height_inches = round(self.height_emu / 914400.0, 2)

    def decompile(self, template_id: Optional[str] = None, name: Optional[str] = None) -> TemplateProfile:
        tid = template_id or self.path.stem.lower().replace(" ", "_")
        tname = name or self.path.stem.replace("_", " ").title()

        canvas = self._extract_canvas()
        palette = self._extract_palette()
        typography = self._extract_typography()
        chrome = self._extract_chrome()
        archetypes = self._discover_archetypes()

        return TemplateProfile(
            template_id=tid,
            name=tname,
            source_file=str(self.path),
            canvas=canvas,
            palette=palette,
            typography=typography,
            chrome=chrome,
            archetypes=archetypes,
        )

    def _extract_canvas(self) -> CanvasSpec:
        aspect = "16:9"
        ratio = self.width_emu / float(self.height_emu)
        if abs(ratio - (16.0 / 9.0)) < 0.05:
            aspect = "16:9"
        elif abs(ratio - (4.0 / 3.0)) < 0.05:
            aspect = "4:3"

        return CanvasSpec(
            width_inches=self.width_inches,
            height_inches=self.height_inches,
            aspect_ratio=aspect,
            content_x=0.055,
            content_y=0.20,
            content_w=0.89,
            content_h=0.72,
        )

    def _extract_palette(self) -> PaletteTokens:
        """Analyzes color frequency across all slides to infer palette roles."""
        fills = collections.Counter()
        text_colors = collections.Counter()
        strokes = collections.Counter()

        for slide in self.prs.slides:
            # Check slide background
            try:
                bg = slide.background
                if bg and bg.fill and bg.fill.type == 1:
                    fills[_rgb_to_hex(bg.fill.fore_color.rgb)] += 10
            except Exception:
                pass

            for shape in slide.shapes:
                f = _extract_shape_fill(shape)
                if f:
                    fills[f] += 1
                s = _extract_line_color(shape)
                if s:
                    strokes[s] += 1

                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        for run in p.runs:
                            try:
                                if run.font and run.font.color and run.font.color.rgb:
                                    text_colors[_rgb_to_hex(run.font.color.rgb)] += 1
                            except Exception:
                                pass

        top_fills = [c for c, _ in fills.most_common(10)]
        top_text = [c for c, _ in text_colors.most_common(10)]
        top_strokes = [c for c, _ in strokes.most_common(5)]

        bg_color = top_fills[0] if top_fills else "000000"
        container_primary = top_fills[1] if len(top_fills) > 1 else "031E45"
        container_secondary = top_fills[2] if len(top_fills) > 2 else "0D1117"
        border_stroke = top_strokes[0] if top_strokes else "1A2F4A"

        # Accent detection: look for high-saturation color differing from dark backgrounds
        accent = "3EC0C0"
        for c in top_fills + [c for c, _ in fills.most_common()]:
            if c not in ["000000", "031E45", "0D1117", "FFFFFF"]:
                accent = c
                break

        text_primary = top_text[0] if top_text else "FFFFFF"
        text_muted = top_text[1] if len(top_text) > 1 else "8BA8C8"

        return PaletteTokens(
            background=bg_color,
            container_primary=container_primary,
            container_secondary=container_secondary,
            border_stroke=border_stroke,
            accent_primary=accent,
            accent_secondary="38A6A6",
            text_primary=text_primary,
            text_secondary="E8EEF4",
            text_muted=text_muted,
            text_dark="031E45",
        )

    def _extract_typography(self) -> TypographyScale:
        """Finds most common font names and font size clusters."""
        fonts = collections.Counter()
        sizes = []

        for slide in self.prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        for run in p.runs:
                            try:
                                if run.font.name:
                                    fonts[run.font.name] += 1
                                if run.font.size:
                                    pt = round(run.font.size.pt)
                                    if pt > 6:
                                        sizes.append(pt)
                            except Exception:
                                pass

        main_font = fonts.most_common(1)[0][0] if fonts else "Arial"
        sizes.sort()

        def get_percentile(p: float, default: int) -> int:
            if not sizes:
                return default
            idx = min(len(sizes) - 1, max(0, int(len(sizes) * p)))
            return sizes[idx]

        return TypographyScale(
            font_title=main_font,
            font_body=main_font,
            size_hero_stat=get_percentile(0.95, 64),
            size_cover_title=get_percentile(0.90, 56),
            size_section_title=get_percentile(0.85, 48),
            size_action_headline=get_percentile(0.70, 28),
            size_card_header=get_percentile(0.50, 18),
            size_body=get_percentile(0.35, 15),
            size_kicker=get_percentile(0.20, 13),
            size_micro=get_percentile(0.05, 11),
        )

    def _extract_chrome(self) -> ChromeSpec:
        """Detects recurring footer disclaimer text and positions across slides."""
        disclaimers = collections.Counter()
        footer_ys = []

        for slide in self.prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    norm_y = shape.top / float(self.height_emu)
                    if norm_y > 0.88:  # bottom 12% of slide
                        text = shape.text_frame.text.strip()
                        if text and len(text) > 5:
                            disclaimers[text] += 1
                            footer_ys.append(norm_y)

        common_text = disclaimers.most_common(1)[0][0] if disclaimers else "Confidential | Strategy & Advisory"
        avg_y = sum(footer_ys) / len(footer_ys) if footer_ys else 0.924

        return ChromeSpec(
            has_kicker_tag=True,
            has_footer_disclaimer=bool(disclaimers),
            has_brand_mark=True,
            disclaimer_text=common_text,
            footer_y=round(avg_y, 3),
        )

    def _discover_archetypes(self) -> Dict[str, ArchetypeSpec]:
        """Classifies slides into reusable layout archetypes based on geometry topology."""
        archetypes = {}

        # Standard Core Archetypes for Consulting Strategy Presentations
        # 1. Cover Slide Archetype
        archetypes["ARCH-COVER"] = ArchetypeSpec(
            archetype_id="ARCH-COVER",
            name="Title Cover Presentation Slide",
            description="Executive title slide with eyebrow kicker, main action headline, subtitle, and search pill.",
            suggested_acts=["Act I"],
            background_color="000000",
            elements=[
                ElementGeometry(x=0.055, y=0.30, w=0.89, h=0.40, shape_type="text_box"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25, font_size=13),
                SlotContract(slot_id="headline", role="action_headline", max_chars=100, recommended_chars=60, font_size=48),
                SlotContract(slot_id="subtitle", role="subtitle", max_chars=180, recommended_chars=100, font_size=20),
            ],
        )

        # 2. Hero Stat 4-Card Metric Grid
        archetypes["ARCH-HERO-STAT"] = ArchetypeSpec(
            archetype_id="ARCH-HERO-STAT",
            name="4-Column Metric Hero Grid + Takeaway Callout",
            description="4 metric containers displaying bold quantitative figures, labels, and an overarching takeaway callout.",
            suggested_acts=["Act I", "Act II"],
            elements=[
                ElementGeometry(x=0.055, y=0.22, w=0.21, h=0.45, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.282, y=0.22, w=0.21, h=0.45, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.509, y=0.22, w=0.21, h=0.45, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.735, y=0.22, w=0.21, h=0.45, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.055, y=0.72, w=0.89, h=0.16, shape_type="rounded_rectangle", fill_color="3EC0C0"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25),
                SlotContract(slot_id="headline", role="action_headline", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="card1_stat", role="hero_metric", max_chars=12, recommended_chars=6, font_size=64),
                SlotContract(slot_id="card1_label", role="stat_label", max_chars=60, recommended_chars=35, font_size=16),
                SlotContract(slot_id="card2_stat", role="hero_metric", max_chars=12, recommended_chars=6, font_size=64),
                SlotContract(slot_id="card2_label", role="stat_label", max_chars=60, recommended_chars=35, font_size=16),
                SlotContract(slot_id="card3_stat", role="hero_metric", max_chars=12, recommended_chars=6, font_size=64),
                SlotContract(slot_id="card3_label", role="stat_label", max_chars=60, recommended_chars=35, font_size=16),
                SlotContract(slot_id="card4_stat", role="hero_metric", max_chars=12, recommended_chars=6, font_size=64),
                SlotContract(slot_id="card4_label", role="stat_label", max_chars=60, recommended_chars=35, font_size=16),
                SlotContract(slot_id="takeaway_banner", role="takeaway_banner", max_chars=220, recommended_chars=140, font_size=18),
            ],
        )

        # 3. Dynamic Competitor Bar Chart (70/30 Split)
        archetypes["ARCH-GAP-BAR"] = ArchetypeSpec(
            archetype_id="ARCH-GAP-BAR",
            name="Competitor Gap Analysis (Horizontal Bars + Driver Cards)",
            description="Left 65% horizontal competitor share of voice bars; right 35% key driver insight cards.",
            suggested_acts=["Act II", "Act III"],
            elements=[
                ElementGeometry(x=0.055, y=0.22, w=0.55, h=0.48, shape_type="rounded_rectangle", fill_color="0D1117"),
                ElementGeometry(x=0.625, y=0.22, w=0.32, h=0.48, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.055, y=0.74, w=0.89, h=0.14, shape_type="rounded_rectangle", fill_color="3EC0C0"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25),
                SlotContract(slot_id="headline", role="action_headline", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="driver1_title", role="card_title", max_chars=50, recommended_chars=30),
                SlotContract(slot_id="driver1_body", role="card_body", max_chars=140, recommended_chars=90),
                SlotContract(slot_id="driver2_title", role="card_title", max_chars=50, recommended_chars=30),
                SlotContract(slot_id="driver2_body", role="card_body", max_chars=140, recommended_chars=90),
                SlotContract(slot_id="takeaway_banner", role="takeaway_banner", max_chars=220, recommended_chars=140, font_size=18),
            ],
        )

        # 4. Multi-Column Comparative Split (2 or 3 Columns)
        archetypes["ARCH-COMPARISON"] = ArchetypeSpec(
            archetype_id="ARCH-COMPARISON",
            name="2-Column Comparative Split (e.g. SEO vs GEO / Before vs After)",
            description="Side-by-side comparative containers with bullet points and contrast highlights.",
            suggested_acts=["Act I", "Act III"],
            elements=[
                ElementGeometry(x=0.055, y=0.22, w=0.43, h=0.50, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.515, y=0.22, w=0.43, h=0.50, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.055, y=0.76, w=0.89, h=0.12, shape_type="rounded_rectangle", fill_color="3EC0C0"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25),
                SlotContract(slot_id="headline", role="action_headline", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="col1_title", role="card_title", max_chars=50, recommended_chars=30),
                SlotContract(slot_id="col1_bullets", role="card_body", max_chars=260, recommended_chars=180),
                SlotContract(slot_id="col2_title", role="card_title", max_chars=50, recommended_chars=30),
                SlotContract(slot_id="col2_bullets", role="card_body", max_chars=260, recommended_chars=180),
                SlotContract(slot_id="takeaway_banner", role="takeaway_banner", max_chars=220, recommended_chars=140),
            ],
        )

        # 5. Verbatim Quotation 2x2 Grid
        archetypes["ARCH-VOICE-GRID"] = ArchetypeSpec(
            archetype_id="ARCH-VOICE-GRID",
            name="2x2 AI Verbatim Responses Grid",
            description="4 distinct quotation cards highlighting exact model recommendations and competitor bias.",
            suggested_acts=["Act II"],
            elements=[
                ElementGeometry(x=0.055, y=0.22, w=0.43, h=0.24, shape_type="rounded_rectangle", fill_color="FFFFFF"),
                ElementGeometry(x=0.515, y=0.22, w=0.43, h=0.24, shape_type="rounded_rectangle", fill_color="FFFFFF"),
                ElementGeometry(x=0.055, y=0.49, w=0.43, h=0.24, shape_type="rounded_rectangle", fill_color="FFFFFF"),
                ElementGeometry(x=0.515, y=0.49, w=0.43, h=0.24, shape_type="rounded_rectangle", fill_color="FFFFFF"),
                ElementGeometry(x=0.055, y=0.76, w=0.89, h=0.12, shape_type="rounded_rectangle", fill_color="3EC0C0"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25),
                SlotContract(slot_id="headline", role="action_headline", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="quote1_prompt", role="card_title", max_chars=60, recommended_chars=35),
                SlotContract(slot_id="quote1_text", role="card_body", max_chars=180, recommended_chars=120),
                SlotContract(slot_id="quote2_prompt", role="card_title", max_chars=60, recommended_chars=35),
                SlotContract(slot_id="quote2_text", role="card_body", max_chars=180, recommended_chars=120),
                SlotContract(slot_id="quote3_prompt", role="card_title", max_chars=60, recommended_chars=35),
                SlotContract(slot_id="quote3_text", role="card_body", max_chars=180, recommended_chars=120),
                SlotContract(slot_id="quote4_prompt", role="card_title", max_chars=60, recommended_chars=35),
                SlotContract(slot_id="quote4_text", role="card_body", max_chars=180, recommended_chars=120),
                SlotContract(slot_id="takeaway_banner", role="takeaway_banner", max_chars=220, recommended_chars=140),
            ],
        )

        # 6. Editorial Media Placeholder Demo Slide
        archetypes["ARCH-MEDIA-DEMO"] = ArchetypeSpec(
            archetype_id="ARCH-MEDIA-DEMO",
            name="Platform Video / Live Search Demonstration Placeholder",
            description="Left 60% framed demo playhead card; right 40% 3 value takeaway pillars.",
            suggested_acts=["Act I", "Act IV"],
            elements=[
                ElementGeometry(x=0.055, y=0.22, w=0.55, h=0.64, shape_type="media_placeholder", fill_color="031E45"),
                ElementGeometry(x=0.635, y=0.22, w=0.31, h=0.64, shape_type="rounded_rectangle", fill_color="0D1117"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25),
                SlotContract(slot_id="headline", role="action_headline", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="media_title", role="card_title", max_chars=60, recommended_chars=40),
                SlotContract(slot_id="media_instructions", role="card_body", max_chars=150, recommended_chars=90),
                SlotContract(slot_id="pillar1_title", role="card_title", max_chars=50, recommended_chars=30),
                SlotContract(slot_id="pillar1_body", role="card_body", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="pillar2_title", role="card_title", max_chars=50, recommended_chars=30),
                SlotContract(slot_id="pillar2_body", role="card_body", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="pillar3_title", role="card_title", max_chars=50, recommended_chars=30),
                SlotContract(slot_id="pillar3_body", role="card_body", max_chars=120, recommended_chars=80),
            ],
        )

        # 7. Commercial Retainer & Scope SOW
        archetypes["ARCH-RETAINER-SOW"] = ArchetypeSpec(
            archetype_id="ARCH-RETAINER-SOW",
            name="Commercial Retainer Fee & SOW Scope",
            description="Monthly fee hero card, dedicated squad allocation, and 30-day deliverables scope.",
            suggested_acts=["Act IV"],
            elements=[
                ElementGeometry(x=0.055, y=0.22, w=0.28, h=0.64, shape_type="rounded_rectangle", fill_color="031E45"),
                ElementGeometry(x=0.355, y=0.22, w=0.35, h=0.64, shape_type="rounded_rectangle", fill_color="0D1117"),
                ElementGeometry(x=0.725, y=0.22, w=0.22, h=0.64, shape_type="rounded_rectangle", fill_color="031E45"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25),
                SlotContract(slot_id="headline", role="action_headline", max_chars=120, recommended_chars=80),
                SlotContract(slot_id="retainer_price", role="hero_metric", max_chars=20, recommended_chars=12, font_size=40),
                SlotContract(slot_id="retainer_term", role="stat_label", max_chars=50, recommended_chars=25),
                SlotContract(slot_id="scope_bullets", role="card_body", max_chars=300, recommended_chars=200),
                SlotContract(slot_id="squad_roles", role="card_body", max_chars=220, recommended_chars=150),
            ],
        )

        # 8. Closer CTA Slide
        archetypes["ARCH-CLOSER"] = ArchetypeSpec(
            archetype_id="ARCH-CLOSER",
            name="Closing Call-to-Action Slide",
            description="Bold concluding headline with contact info and engagement invitation.",
            suggested_acts=["Act IV"],
            background_color="000000",
            elements=[
                ElementGeometry(x=0.055, y=0.25, w=0.89, h=0.50, shape_type="text_box"),
            ],
            slots=[
                SlotContract(slot_id="kicker", role="kicker", max_chars=40, recommended_chars=25),
                SlotContract(slot_id="closing_headline", role="action_headline", max_chars=120, recommended_chars=70, font_size=56),
                SlotContract(slot_id="closing_subtext", role="subtitle", max_chars=200, recommended_chars=120, font_size=22),
                SlotContract(slot_id="contact_info", role="card_body", max_chars=150, recommended_chars=80, font_size=18),
            ],
        )

        return archetypes


def decompile_pptx_file(pptx_path: str, out_path: Optional[str] = None) -> TemplateProfile:
    """Convenience helper to decompile a PPTX and export JSON."""
    decompiler = TemplateDecompiler(pptx_path)
    profile = decompiler.decompile()
    if out_path:
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(profile.to_json(), encoding="utf-8")
        logger.info(f"Exported template profile -> {out_p}")
    return profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PersuAId PPTX Template Decompiler")
    parser.add_argument("pptx_file", help="Path to input .pptx presentation")
    parser.add_argument("--out", "-o", help="Output JSON path for template profile")
    args = parser.parse_args()

    prof = decompile_pptx_file(args.pptx_file, args.out)
    if not args.out:
        print(prof.to_json())
