#!/usr/bin/env python3
"""
PersuAId Universal Presentation Compiler
Compiles staged Act-by-Act presentation sessions into native OpenXML .pptx files
using normalized unit-space geometry, palette tokens, and layout archetypes.
"""

import copy
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pptx
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.copy_guard import sanitize_generated_copy
from engine.staging_manager import DeckStagingManager
from engine.template_profile import ArchetypeSpec, TemplateProfile

logger = logging.getLogger("universal-compiler")


def _clone_first_ppr(tf):
    """Deep-copy the first <a:pPr> (alignment, indent, line spacing) in the text frame."""
    for p in tf.paragraphs:
        ppr = p._p.find(qn("a:pPr"))
        if ppr is not None:
            return copy.deepcopy(ppr)
    return None


def _clone_first_rpr(tf):
    """Deep-copy the first <a:rPr> (font family, weight, kerning, color, size) in the frame."""
    for p in tf.paragraphs:
        for r in p.runs:
            rpr = r._r.find(qn("a:rPr"))
            if rpr is not None:
                return copy.deepcopy(rpr)
        end_rpr = p._p.find(qn("a:endParaRPr"))
        if end_rpr is not None:
            clone = copy.deepcopy(end_rpr)
            clone.tag = qn("a:rPr")
            return clone
    return None


def _apply_ppr(paragraph, ppr) -> None:
    if ppr is None:
        return
    p_el = paragraph._p
    existing = p_el.find(qn("a:pPr"))
    if existing is not None:
        p_el.remove(existing)
    p_el.insert(0, copy.deepcopy(ppr))


def _apply_rpr(run, rpr) -> None:
    if rpr is None:
        return
    r_el = run._r
    existing = r_el.find(qn("a:rPr"))
    if existing is not None:
        r_el.remove(existing)
    r_el.insert(0, copy.deepcopy(rpr))


def _set_textframe(tf, text: str, *, bold_first: bool = False, size_pt: Optional[int] = None, font_name: Optional[str] = None, color_rgb: Optional[RGBColor] = None) -> None:
    """
    Replace text in a text frame while preserving the template's typography.
    Avoids python-pptx's default Calibri black behavior by copying and re-applying properties.
    """
    cleaned_text = sanitize_generated_copy(text)
    src_ppr = _clone_first_ppr(tf)
    src_rpr = _clone_first_rpr(tf)

    tf.clear()
    lines = cleaned_text.split("\n") if cleaned_text else [""]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        _apply_ppr(p, src_ppr)
        for r in p.runs:
            _apply_rpr(r, src_rpr)
            if size_pt:
                r.font.size = Pt(size_pt)
            if font_name:
                r.font.name = font_name
            if color_rgb:
                r.font.color.rgb = color_rgb
            if bold_first and i == 0:
                r.font.bold = True


def _hex_to_rgb(hex_str: str) -> RGBColor:
    clean = hex_str.strip().lstrip("#")
    if len(clean) != 6:
        clean = "FFFFFF"
    r = int(clean[0:2], 16)
    g = int(clean[2:4], 16)
    b = int(clean[4:6], 16)
    return RGBColor(r, g, b)


class UniversalDeckCompiler:
    """Compiles a DeckStagingManager session into a high-fidelity native PPTX presentation."""

    def __init__(self, staging_manager: Optional[DeckStagingManager] = None):
        self.mgr = staging_manager or DeckStagingManager()

    def compile_session(
        self,
        session_id: str,
        out_dir: str = ".",
    ) -> Dict[str, Any]:
        session = self.mgr.get_session(session_id)
        template = self.mgr.get_template(session.get("template_source") or session.get("template_id", "default"))

        # Use source presentation if available to retain custom master layouts, background art, and styles
        source_file = getattr(template, "source_file", None)
        if source_file and Path(source_file).exists():
            try:
                prs = Presentation(str(source_file))
            except Exception as e:
                logger.warning(f"Could not load source template {source_file}: {e}. Falling back to clean presentation.")
                prs = Presentation()
                prs.slide_width = Inches(template.canvas.width_inches)
                prs.slide_height = Inches(template.canvas.height_inches)
        else:
            prs = Presentation()
            # Set Canvas Dimensions
            prs.slide_width = Inches(template.canvas.width_inches)
            prs.slide_height = Inches(template.canvas.height_inches)

        # Check if we are hydrating an uploaded custom presentation
        is_custom_source = bool(source_file and Path(source_file).exists())
        template_slides_count = len(prs.slides) if is_custom_source else 0

        blank_layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[0]

        brand = session.get("brand", "Executive")
        slides_dict = session.get("slides", {})
        sorted_slide_keys = sorted(slides_dict.keys(), key=lambda k: int(k))

        used_template_indices = set()

        for idx, key in enumerate(sorted_slide_keys):
            slide_data = slides_dict[key]
            slide_no = slide_data.get("slide_number", int(key))
            arch_id = slide_data.get("archetype_id", "ARCH-HERO-STAT")
            slots = slide_data.get("slots", {})
            arch = template.archetypes.get(arch_id)

            # If this is a custom slide layout (e.g. ARCH-SLIDE-1, ARCH-SLIDE-2) and exists in template
            if is_custom_source and arch_id.startswith("ARCH-SLIDE-"):
                try:
                    src_slide_idx = int(arch_id.split("-")[-1]) - 1
                except ValueError:
                    src_slide_idx = idx

                if 0 <= src_slide_idx < template_slides_count:
                    target_slide = prs.slides[src_slide_idx]
                    used_template_indices.add(src_slide_idx)
                    self._hydrate_template_slide_inplace(target_slide, arch, slots)
                    continue

            # Otherwise, render fresh slide on canvas (standard Redcomm consulting archetypes)
            slide = prs.slides.add_slide(blank_layout)

            # 1. Background Fill
            bg_color = arch.background_color if arch and arch.background_color else template.palette.background
            self._set_background(slide, bg_color)

            # 2. Render Chrome (Header & Footer)
            if arch_id != "ARCH-COVER":
                self._render_chrome(slide, template, brand, slots)

            # 3. Render Archetype Elements & Slots
            if arch_id == "ARCH-COVER":
                self._render_cover(slide, template, brand, slots)
            elif arch_id == "ARCH-HERO-STAT":
                self._render_hero_stat(slide, template, slots)
            elif arch_id == "ARCH-GAP-BAR":
                self._render_gap_bar(slide, template, brand, slots)
            elif arch_id == "ARCH-COMPARISON":
                self._render_comparison(slide, template, slots)
            elif arch_id == "ARCH-VOICE-GRID":
                self._render_voice_grid(slide, template, slots)
            elif arch_id == "ARCH-MEDIA-DEMO":
                self._render_media_demo(slide, template, slots)
            elif arch_id == "ARCH-RETAINER-SOW":
                self._render_retainer_sow(slide, template, slots)
            elif arch_id == "ARCH-CLOSER":
                self._render_closer(slide, template, brand, slots)
            else:
                self._render_generic_archetype(slide, template, arch, slots)

        # In custom template mode, remove unused original template slides
        if is_custom_source and used_template_indices:
            all_slide_ids = list(prs.slides._sldIdLst)
            for s_idx, sld_elem in enumerate(all_slide_ids):
                if s_idx not in used_template_indices:
                    try:
                        prs.slides._sldIdLst.remove(sld_elem)
                    except Exception:
                        pass

        out_path = Path(out_dir)
        try:
            out_path.mkdir(parents=True, exist_ok=True)
            test_file = out_path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError):
            for fallback in [Path("/app/data"), Path("/tmp/persuaid_decks"), Path(".")]:
                try:
                    fallback.mkdir(parents=True, exist_ok=True)
                    out_path = fallback
                    break
                except Exception:
                    pass

        brand_slug = brand.replace(" ", "_").replace(".", "")
        deck_filename = f"{brand_slug}_GEO_Executive_Deck.pptx"
        dest_file = out_path / deck_filename
        prs.save(str(dest_file))

        import base64
        file_bytes = dest_file.read_bytes()
        file_size_kb = round(len(file_bytes) / 1024.0, 1)
        deck_base64 = base64.b64encode(file_bytes).decode("ascii")

        return {
            "status": "success",
            "session_id": session_id,
            "brand": brand,
            "filename": deck_filename,
            "total_slides": len(sorted_slide_keys),
            "deck_path": str(dest_file.resolve()),
            "file_size_kb": file_size_kb,
            "deck_base64": deck_base64,
            "message": f"Successfully compiled {len(sorted_slide_keys)}-slide native PPTX deck for {brand} -> {dest_file} ({file_size_kb} KB). Base64 presentation payload included in 'deck_base64' for direct client workspace writing.",
        }

    def _hydrate_template_slide_inplace(
        self,
        slide: Any,
        arch: Optional[ArchetypeSpec],
        slots: Dict[str, Any],
    ) -> None:
        """Fills an existing template slide's text shapes in-place using _set_textframe."""
        text_shapes = [s for s in slide.shapes if s.has_text_frame]

        # Map slot keys to shapes
        for s_idx, shape in enumerate(text_shapes, start=1):
            slot_key = f"slot_{s_idx}"
            val = slots.get(slot_key)

            # Check semantic mappings for headline or kicker
            if val is None and s_idx == 1 and "headline" in slots:
                val = slots.get("headline")
            elif val is None and s_idx == 2 and "kicker" in slots:
                val = slots.get("kicker")

            if val is not None and str(val).strip():
                _set_textframe(shape.text_frame, str(val))

    def _set_background(self, slide: Any, hex_color: str) -> None:
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = _hex_to_rgb(hex_color)

    def _render_chrome(
        self,
        slide: Any,
        template: TemplateProfile,
        brand: str,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        # Header Eyebrow Kicker & Action Headline
        kicker = slots.get("kicker", "EXECUTIVE DIAGNOSIS")
        headline = slots.get("headline", "")

        tx_box = slide.shapes.add_textbox(
            Inches(template.canvas.content_x * W),
            Inches(0.06 * H),
            Inches(template.canvas.content_w * W),
            Inches(0.12 * H),
        )
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = str(kicker).upper()
        p1.font.name = template.typography.font_title
        p1.font.size = Pt(template.typography.size_kicker)
        p1.font.bold = True
        p1.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        if headline:
            p2 = tf.add_paragraph()
            p2.text = str(headline)
            p2.font.name = template.typography.font_title
            p2.font.size = Pt(template.typography.size_action_headline)
            p2.font.bold = True
            p2.font.color.rgb = _hex_to_rgb(template.palette.text_primary)
            p2.space_before = Pt(4)

        # Footer Disclaimer (Matching exact reference styling: pure white, 11pt, multi-line)
        if template.chrome.has_footer_disclaimer:
            disclaimer = slide.shapes.add_textbox(
                Inches(template.canvas.content_x * W),
                Inches(template.chrome.footer_y * H),
                Inches(0.60 * W),
                Inches(0.06 * H),
            )
            dtf = disclaimer.text_frame
            dtf.word_wrap = True
            dtf.margin_left = dtf.margin_top = dtf.margin_right = dtf.margin_bottom = 0
            dp = dtf.paragraphs[0]
            dp.text = template.chrome.disclaimer_text
            dp.font.name = template.typography.font_body
            dp.font.size = Pt(template.typography.size_micro)
            # Driven purely by template chrome token
            dp.font.color.rgb = _hex_to_rgb(template.chrome.disclaimer_color)

        # Brand Mark Pill (Bottom Right)
        if template.chrome.has_brand_mark:
            pill = slide.shapes.add_textbox(
                Inches((template.canvas.content_x + template.canvas.content_w - 0.20) * W),
                Inches(template.chrome.footer_y * H),
                Inches(0.20 * W),
                Inches(0.06 * H),
            )
            ptf = pill.text_frame
            ptf.margin_left = ptf.margin_top = ptf.margin_right = ptf.margin_bottom = 0
            pp = ptf.paragraphs[0]
            pp.alignment = PP_ALIGN.RIGHT
            pp.text = f"{brand} · 2026"
            pp.font.name = template.typography.font_body
            pp.font.size = Pt(11)
            pp.font.bold = True
            pp.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

    def _render_cover(
        self,
        slide: Any,
        template: TemplateProfile,
        brand: str,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        kicker = slots.get("kicker", "CONFIDENTIAL EXECUTIVE BRIEFING")
        headline = slots.get("headline", f"THE NEW BATTLE FOR AI SEARCH VISIBILITY · {brand.upper()}")
        subtitle = slots.get("subtitle", "Generative Engine Optimization (GEO) Audit & 6-Month Retainer Strategy")

        tb = slide.shapes.add_textbox(Inches(0.08 * W), Inches(0.25 * H), Inches(0.84 * W), Inches(0.45 * H))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = str(kicker).upper()
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        p2 = tf.add_paragraph()
        p2.text = str(headline)
        p2.font.size = Pt(template.typography.size_cover_title)
        p2.font.bold = True
        p2.font.color.rgb = _hex_to_rgb(template.palette.text_primary)
        p2.space_before = Pt(12)

        p3 = tf.add_paragraph()
        p3.text = str(subtitle)
        p3.font.size = Pt(20)
        p3.font.color.rgb = _hex_to_rgb(template.palette.text_muted)
        p3.space_before = Pt(16)

        # Search Bar Graphic Container
        sb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.08 * W), Inches(0.72 * H), Inches(0.84 * W), Inches(0.12 * H))
        sb.fill.solid()
        sb.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
        sb.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)
        sbt = sb.text_frame
        sbt.margin_left = Inches(0.3)
        sbp = sbt.paragraphs[0]
        sbp.text = f"🔍  What is the best {slots.get('category', 'choice')} in Indonesia?  |  AI Overview: {brand} Presence Analysis"
        sbp.font.size = Pt(18)
        sbp.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)

    def _render_hero_stat(
        self,
        slide: Any,
        template: TemplateProfile,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        cards = [
            ("card1_stat", "card1_label"),
            ("card2_stat", "card2_label"),
            ("card3_stat", "card3_label"),
            ("card4_stat", "card4_label"),
        ]

        card_w = 0.205
        gap = 0.023
        start_x = template.canvas.content_x

        for i, (stat_key, label_key) in enumerate(cards):
            x = start_x + i * (card_w + gap)
            shape = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(x * W),
                Inches(0.20 * H),
                Inches(card_w * W),
                Inches(0.48 * H),
            )
            shape.fill.solid()
            # Driven purely by template tokens - zero hardcoded hex
            shape.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
            shape.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)
            shape.line.width = Pt(1.5)

            tf = shape.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP
            tf.margin_left = tf.margin_right = Inches(0.25)
            tf.margin_top = Inches(0.35)

            p_val = tf.paragraphs[0]
            p_val.text = str(slots.get(stat_key, "--"))
            p_val.font.size = Pt(template.typography.size_hero_stat)
            p_val.font.bold = True
            p_val.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

            p_lbl = tf.add_paragraph()
            # Remove trailing periods from labels
            label_text = str(slots.get(label_key, "Benchmark Metric")).rstrip(".")
            p_lbl.text = label_text
            p_lbl.font.size = Pt(template.typography.size_card_header)
            p_lbl.font.bold = True
            p_lbl.font.color.rgb = _hex_to_rgb(template.palette.text_primary)
            p_lbl.space_before = Pt(14)

        # Solid Cyan Takeaway Banner
        self._add_takeaway_banner(slide, template, slots.get("takeaway_banner", ""))

    def _render_gap_bar(
        self,
        slide: Any,
        template: TemplateProfile,
        brand: str,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        # Left Container (Bar Chart Container with visual benchmark bars)
        c_left = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(template.canvas.content_x * W),
            Inches(0.22 * H),
            Inches(0.55 * W),
            Inches(0.48 * H),
        )
        c_left.fill.solid()
        c_left.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_secondary)
        c_left.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)

        ltf = c_left.text_frame
        ltf.word_wrap = True
        ltf.margin_left = ltf.margin_right = Inches(0.25)
        ltf.margin_top = Inches(0.2)

        lp_h = ltf.paragraphs[0]
        lp_h.text = "CATEGORY AI SHARE OF VOICE & CITATION GAP"
        lp_h.font.bold = True
        lp_h.font.size = Pt(15)
        lp_h.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        # Draw benchmark bar representations
        benchmarks = [
            (brand, slots.get("client_sov", "22.4%"), "95% consensus mentions", template.palette.accent_primary),
            (slots.get("comp1_name", "Mobil88"), slots.get("comp1_sov", "18.4%"), "Leading high-intent citations", "8BA8C8"),
            (slots.get("comp2_name", "Carmudi"), slots.get("comp2_sov", "14.2%"), "Spec pages & pricing consensus", "8BA8C8"),
            (slots.get("comp3_name", "Carsome"), slots.get("comp3_sov", "9.8%"), "Certified inspection focus", "8BA8C8"),
        ]

        for b_name, b_val, b_desc, b_color in benchmarks:
            bp = ltf.add_paragraph()
            bp.text = f"■ {b_name}: {b_val} — {b_desc}"
            bp.font.size = Pt(13)
            bp.font.color.rgb = _hex_to_rgb(b_color)
            bp.space_before = Pt(8)

        # Right Container (Driver Cards)
        c_right = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.625 * W),
            Inches(0.22 * H),
            Inches(0.32 * W),
            Inches(0.48 * H),
        )
        c_right.fill.solid()
        c_right.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
        c_right.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)

        rtf = c_right.text_frame
        rtf.word_wrap = True
        rtf.margin_left = rtf.margin_right = Inches(0.25)
        rtf.margin_top = Inches(0.25)

        p_h = rtf.paragraphs[0]
        p_h.text = "WHY DOES THIS HAPPEN?"
        p_h.font.bold = True
        p_h.font.size = Pt(16)
        p_h.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        d1_t = slots.get("driver1_title", "Aggregator Hegemony")
        d1_b = slots.get("driver1_body", "Third-party comparison platforms capture top citations before brand domain.")
        p_d1 = rtf.add_paragraph()
        p_d1.text = f"• {d1_t}: {d1_b}"
        p_d1.font.size = Pt(14)
        p_d1.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)
        p_d1.space_before = Pt(8)

        d2_t = slots.get("driver2_title", "Crawler Gaps")
        d2_b = slots.get("driver2_body", "Dynamic client-side hydration prevents complete LLM indexing.")
        p_d2 = rtf.add_paragraph()
        p_d2.text = f"• {d2_t}: {d2_b}"
        p_d2.font.size = Pt(14)
        p_d2.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)
        p_d2.space_before = Pt(8)

        self._add_takeaway_banner(slide, template, slots.get("takeaway_banner", ""))

    def _render_comparison(
        self,
        slide: Any,
        template: TemplateProfile,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        cols = [
            ("col1_title", "col1_body", "col1_bullets", template.canvas.content_x),
            ("col2_title", "col2_body", "col2_bullets", 0.515),
        ]

        for title_k, body_k, bullets_k, col_x in cols:
            box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(col_x * W),
                Inches(0.20 * H),
                Inches(0.43 * W),
                Inches(0.50 * H),
            )
            box.fill.solid()
            box.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
            box.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)

            tf = box.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP
            tf.margin_left = tf.margin_right = Inches(0.4)
            tf.margin_top = Inches(0.4)
            tf.margin_bottom = Inches(0.4)

            p_t = tf.paragraphs[0]
            p_t.text = str(slots.get(title_k, "Dimension"))
            p_t.font.bold = True
            p_t.font.size = Pt(22)
            p_t.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

            body_content = str(slots.get(body_k) or slots.get(bullets_k) or "")
            if body_content:
                lines = [line.strip() for line in body_content.split("\n") if line.strip()]
                for line in lines:
                    p_b = tf.add_paragraph()
                    p_b.text = line
                    p_b.font.size = Pt(18)
                    p_b.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)
                    p_b.space_before = Pt(14)

        self._add_takeaway_banner(slide, template, slots.get("takeaway_banner", ""), banner_y=0.73, banner_h=0.14)

    def _render_voice_grid(
        self,
        slide: Any,
        template: TemplateProfile,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        quotes = [
            ("quote1_prompt", "quote1_text", template.canvas.content_x, 0.22),
            ("quote2_prompt", "quote2_text", 0.515, 0.22),
            ("quote3_prompt", "quote3_text", template.canvas.content_x, 0.48),
            ("quote4_prompt", "quote4_text", 0.515, 0.48),
        ]

        for p_key, t_key, qx, qy in quotes:
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(qx * W),
                Inches(qy * H),
                Inches(0.43 * W),
                Inches(0.24 * H),
            )
            # Pristine white card aesthetic
            card.fill.solid()
            card.fill.fore_color.rgb = _hex_to_rgb("FFFFFF")
            card.line.color.rgb = _hex_to_rgb("E2E8F0")

            tf = card.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = Inches(0.2)
            tf.margin_top = Inches(0.15)

            # Resolve prompt and quote with fallback to theme keys
            prompt_val = slots.get(p_key) or slots.get(f"theme{quotes.index((p_key, t_key, qx, qy))+1}_title") or "Search intent"
            quote_val = slots.get(t_key) or slots.get(f"theme{quotes.index((p_key, t_key, qx, qy))+1}_body") or "AI recommendation analysis"

            p_prompt = tf.paragraphs[0]
            p_prompt.text = f"FOCUS: {prompt_val}"
            p_prompt.font.bold = True
            p_prompt.font.size = Pt(12)
            p_prompt.font.color.rgb = _hex_to_rgb(template.palette.accent_secondary)

            p_quote = tf.add_paragraph()
            p_quote.text = f"“{quote_val}”"
            p_quote.font.size = Pt(14)
            p_quote.font.color.rgb = _hex_to_rgb(template.palette.text_dark)
            p_quote.space_before = Pt(6)

        self._add_takeaway_banner(slide, template, slots.get("takeaway_banner", ""))

    def _render_media_demo(
        self,
        slide: Any,
        template: TemplateProfile,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        # Left 60% Demo Frame (Editorial media placeholder)
        frame = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(template.canvas.content_x * W),
            Inches(0.22 * H),
            Inches(0.55 * W),
            Inches(0.66 * H),
        )
        frame.fill.solid()
        frame.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
        frame.line.color.rgb = _hex_to_rgb(template.palette.accent_primary)
        frame.line.width = Pt(1.5)

        ftf = frame.text_frame
        ftf.word_wrap = True
        ftf.margin_left = ftf.margin_right = Inches(0.3)
        ftf.margin_top = Inches(0.4)

        fp1 = ftf.paragraphs[0]
        fp1.text = "▶  LIVE PLATFORM / SEARCH JOURNEY DEMO"
        fp1.font.bold = True
        fp1.font.size = Pt(20)
        fp1.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        fp2 = ftf.add_paragraph()
        fp2.text = str(slots.get("media_title", "Live AI Model Search Journey Recording"))
        fp2.font.bold = True
        fp2.font.size = Pt(16)
        fp2.font.color.rgb = _hex_to_rgb(template.palette.text_primary)
        fp2.space_before = Pt(12)

        fp3 = ftf.add_paragraph()
        fp3.text = str(slots.get("media_instructions", "[Insert MP4 recording / interactive demo screen here]"))
        fp3.font.size = Pt(13)
        fp3.font.color.rgb = _hex_to_rgb(template.palette.text_muted)
        fp3.space_before = Pt(8)

        # Right 35% Value Pillars
        side = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.635 * W),
            Inches(0.22 * H),
            Inches(0.31 * W),
            Inches(0.66 * H),
        )
        side.fill.solid()
        side.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_secondary)
        side.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)

        stf = side.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_right = Inches(0.25)
        stf.margin_top = Inches(0.25)

        sp_h = stf.paragraphs[0]
        sp_h.text = "STRATEGIC IMPLICATIONS"
        sp_h.font.bold = True
        sp_h.font.size = Pt(16)
        sp_h.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        pillars = [
            ("pillar1_title", "pillar1_body"),
            ("pillar2_title", "pillar2_body"),
            ("pillar3_title", "pillar3_body"),
        ]
        for p_t_key, p_b_key in pillars:
            p_title = slots.get(p_t_key, "Key Value Pillar")
            p_body = slots.get(p_b_key, "Actionable strategic driver")
            sp = stf.add_paragraph()
            sp.text = f"• {p_title}: {p_body}"
            sp.font.size = Pt(13)
            sp.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)
            sp.space_before = Pt(10)

    def _render_retainer_sow(
        self,
        slide: Any,
        template: TemplateProfile,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        # Col 1: Retainer Fee Card
        c1 = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(template.canvas.content_x * W),
            Inches(0.22 * H),
            Inches(0.28 * W),
            Inches(0.66 * H),
        )
        c1.fill.solid()
        c1.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
        c1.line.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        c1_tf = c1.text_frame
        c1_tf.word_wrap = True
        c1_tf.margin_left = c1_tf.margin_right = Inches(0.25)
        c1_tf.margin_top = Inches(0.3)

        p1 = c1_tf.paragraphs[0]
        p1.text = "RECOMMENDED MONTHLY RETAINER"
        p1.font.bold = True
        p1.font.size = Pt(14)
        p1.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        p_fee = c1_tf.add_paragraph()
        p_fee.text = str(slots.get("retainer_price", "IDR 25M–35M"))
        p_fee.font.bold = True
        p_fee.font.size = Pt(36)
        p_fee.font.color.rgb = _hex_to_rgb(template.palette.text_primary)
        p_fee.space_before = Pt(12)

        p_term = c1_tf.add_paragraph()
        p_term.text = str(slots.get("retainer_term", "Per Month · 6-Month Commitment"))
        p_term.font.size = Pt(14)
        p_term.font.color.rgb = _hex_to_rgb(template.palette.text_muted)
        p_term.space_before = Pt(4)

        # Col 2: Deliverables Scope
        c2 = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.355 * W),
            Inches(0.22 * H),
            Inches(0.35 * W),
            Inches(0.66 * H),
        )
        c2.fill.solid()
        c2.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_secondary)
        c2.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)
        c2_tf = c2.text_frame
        c2_tf.word_wrap = True
        c2_tf.margin_left = c2_tf.margin_right = Inches(0.25)
        c2_tf.margin_top = Inches(0.3)

        c2_h = c2_tf.paragraphs[0]
        c2_h.text = "CORE SCOPE OF WORK"
        c2_h.font.bold = True
        c2_h.font.size = Pt(14)
        c2_h.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        c2_b = c2_tf.add_paragraph()
        c2_b.text = str(slots.get("scope_bullets", "• Daily AI engine tracking across ChatGPT, Gemini, Perplexity\n• Monthly citation acquisition sprints\n• Technical crawler bot audit & unblocking"))
        c2_b.font.size = Pt(14)
        c2_b.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)
        c2_b.space_before = Pt(10)

        # Col 3: Dedicated Squad Allocation
        c3 = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.725 * W),
            Inches(0.22 * H),
            Inches(0.22 * W),
            Inches(0.66 * H),
        )
        c3.fill.solid()
        c3.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
        c3.line.color.rgb = _hex_to_rgb(template.palette.border_stroke)
        c3_tf = c3.text_frame
        c3_tf.word_wrap = True
        c3_tf.margin_left = c3_tf.margin_right = Inches(0.2)
        c3_tf.margin_top = Inches(0.3)

        c3_h = c3_tf.paragraphs[0]
        c3_h.text = "DEDICATED SQUAD"
        c3_h.font.bold = True
        c3_h.font.size = Pt(14)
        c3_h.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        c3_b = c3_tf.add_paragraph()
        c3_b.text = str(slots.get("squad_roles", "• GEO Strategist\n• Technical SEO Engineer\n• Authority Content Lead\n• Account Director"))
        c3_b.font.size = Pt(13)
        c3_b.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)
        c3_b.space_before = Pt(10)

    def _render_closer(
        self,
        slide: Any,
        template: TemplateProfile,
        brand: str,
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(template.canvas.content_x * W),
            Inches(0.20 * H),
            Inches(template.canvas.content_w * W),
            Inches(0.66 * H),
        )
        card.fill.solid()
        card.fill.fore_color.rgb = _hex_to_rgb(template.palette.container_primary)
        card.line.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.5)
        tf.margin_top = Inches(0.5)

        p1 = tf.paragraphs[0]
        p1.text = str(slots.get("kicker", "THE MANDATE FOR 2026")).upper()
        p1.font.bold = True
        p1.font.size = Pt(16)
        p1.font.color.rgb = _hex_to_rgb(template.palette.accent_primary)

        p2 = tf.add_paragraph()
        p2.text = str(slots.get("closing_headline", f"{brand.upper()} DESERVES TO BE THE AI'S FIRST ANSWER."))
        p2.font.bold = True
        p2.font.size = Pt(36)
        p2.font.color.rgb = _hex_to_rgb(template.palette.text_primary)
        p2.space_before = Pt(16)

        p3 = tf.add_paragraph()
        p3.text = str(slots.get("closing_subtext", "Let's turn AI search visibility into verified showroom footfall and digital inquiries."))
        p3.font.size = Pt(20)
        p3.font.color.rgb = _hex_to_rgb(template.palette.text_secondary)
        p3.space_before = Pt(14)

        if "contact_info" in slots:
            p4 = tf.add_paragraph()
            p4.text = f"Engagement Lead: {slots.get('contact_info')}"
            p4.font.size = Pt(14)
            p4.font.color.rgb = _hex_to_rgb(template.palette.accent_secondary)
            p4.space_before = Pt(20)

    def _render_generic_archetype(
        self,
        slide: Any,
        template: TemplateProfile,
        arch: Optional[ArchetypeSpec],
        slots: Dict[str, Any],
    ) -> None:
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        if not arch or not arch.elements:
            tb = slide.shapes.add_textbox(Inches(0.1 * W), Inches(0.25 * H), Inches(0.8 * W), Inches(0.4 * H))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = str(slots)
            p.font.size = Pt(14)
            p.font.color.rgb = _hex_to_rgb(template.palette.text_primary)
            return

        for el in arch.elements:
            shape = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(el.x * W),
                Inches(el.y * H),
                Inches(el.w * W),
                Inches(el.h * H),
            )
            fill_c = el.fill_color or template.palette.container_primary
            shape.fill.solid()
            shape.fill.fore_color.rgb = _hex_to_rgb(fill_c)
            shape.line.color.rgb = _hex_to_rgb(el.border_color or template.palette.border_stroke)

    def _add_takeaway_banner(
        self,
        slide: Any,
        template: TemplateProfile,
        text: str,
        banner_y: float = 0.74,
        banner_h: float = 0.14,
    ) -> None:
        if not text:
            return
        W = template.canvas.width_inches
        H = template.canvas.height_inches

        banner = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(template.canvas.content_x * W),
            Inches(banner_y * H),
            Inches(template.canvas.content_w * W),
            Inches(banner_h * H),
        )
        banner.fill.solid()
        banner.fill.fore_color.rgb = _hex_to_rgb(template.palette.accent_primary)
        banner.line.color.rgb = _hex_to_rgb(template.palette.accent_secondary)

        tf = banner.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.15)

        p_h = tf.paragraphs[0]
        p_h.text = "EXECUTIVE TAKEAWAY & STRATEGIC MANDATE:"
        p_h.font.bold = True
        p_h.font.size = Pt(13)
        p_h.font.color.rgb = _hex_to_rgb(template.palette.text_dark)

        p_b = tf.add_paragraph()
        p_b.text = str(text)
        p_b.font.bold = True
        p_b.font.size = Pt(16)
        p_b.font.color.rgb = _hex_to_rgb(template.palette.text_dark)
        p_b.space_before = Pt(4)
