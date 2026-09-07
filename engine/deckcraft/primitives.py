#!/usr/bin/env python3
"""
PersuAId DeckCraft Reusable Layout Primitives
Mathematical shape builders, typography managers, and visual components
strictly adhering to the signature Redcomm Indonesia aesthetic.
"""

from typing import List, Optional
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from engine.deckcraft.tokens import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    MARGIN_X,
    MARGIN_Y,
    CONTENT_WIDTH,
    FOOTER_Y,
    COLOR_OBSIDIAN,
    COLOR_NAVY,
    COLOR_CYAN,
    COLOR_CYAN_DEEP,
    COLOR_CARD_SLATE,
    COLOR_CARD_BORDER,
    COLOR_WHITE,
    COLOR_OFF_WHITE,
    COLOR_COOL_GRAY,
    COLOR_MUTED_SLATE,
    COLOR_DARK_TEXT,
    FONT_PRIMARY,
    SIZE_ACTION_TITLE,
    SIZE_KICKER,
    SIZE_HERO_STAT,
    SIZE_CARD_HEADER,
    SIZE_BODY,
    SIZE_BODY_SM,
    SIZE_FOOTER,
)


def set_slide_background(slide, color: RGBColor = COLOR_OBSIDIAN):
    """Fills the slide background with a solid color."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(
    slide,
    kicker: str,
    title: str,
    subtitle: Optional[str] = None,
    centered: bool = True,
    top_y: Inches = MARGIN_Y,
):
    """Adds the standard slide header with cyan eyebrow kicker and action title."""
    # Eyebrow Kicker
    kicker_box = slide.shapes.add_textbox(
        MARGIN_X, top_y, CONTENT_WIDTH, Inches(0.4)
    )
    tf_k = kicker_box.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_right = tf_k.margin_top = tf_k.margin_bottom = 0
    p_k = tf_k.paragraphs[0]
    p_k.text = kicker.upper()
    p_k.font.name = FONT_PRIMARY
    p_k.font.size = SIZE_KICKER
    p_k.font.bold = True
    p_k.font.color.rgb = COLOR_CYAN
    if centered:
        p_k.alignment = PP_ALIGN.CENTER

    # Assertive Action Title
    title_y = top_y + Inches(0.35)
    title_box = slide.shapes.add_textbox(
        MARGIN_X, title_y, CONTENT_WIDTH, Inches(0.8)
    )
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_PRIMARY
    p_t.font.size = SIZE_ACTION_TITLE
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    if centered:
        p_t.alignment = PP_ALIGN.CENTER

    # Optional Subtitle
    if subtitle:
        sub_y = title_y + Inches(0.7)
        sub_box = slide.shapes.add_textbox(
            MARGIN_X, sub_y, CONTENT_WIDTH, Inches(0.4)
        )
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle
        p_s.font.name = FONT_PRIMARY
        p_s.font.size = SIZE_BODY
        p_s.font.color.rgb = COLOR_MUTED_SLATE
        if centered:
            p_s.alignment = PP_ALIGN.CENTER


def add_footer(slide, brand_name: str = "Brand"):
    """Adds the standard confidentiality disclaimer and brand logo pill."""
    # Left disclaimer
    left_box = slide.shapes.add_textbox(
        MARGIN_X, FOOTER_Y, Inches(6.0), Inches(0.45)
    )
    tf_l = left_box.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = 0
    p_l1 = tf_l.paragraphs[0]
    p_l1.text = "Redcomm Indonesia"
    p_l1.font.name = FONT_PRIMARY
    p_l1.font.size = SIZE_FOOTER
    p_l1.font.bold = True
    p_l1.font.color.rgb = COLOR_MUTED_SLATE

    p_l2 = tf_l.add_paragraph()
    p_l2.text = "© 2026. All Rights Reserved. Confidential Do Not Distribute."
    p_l2.font.name = FONT_PRIMARY
    p_l2.font.size = Pt(9.5)
    p_l2.font.color.rgb = COLOR_MUTED_SLATE

    # Right brand mark
    right_box = slide.shapes.add_textbox(
        CANVAS_WIDTH - MARGIN_X - Inches(3.5), FOOTER_Y, Inches(3.5), Inches(0.45)
    )
    tf_r = right_box.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.text = f"२. |  {brand_name}"
    p_r.font.name = FONT_PRIMARY
    p_r.font.size = SIZE_BODY
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_WHITE


def add_card(
    slide,
    x: Inches,
    y: Inches,
    w: Inches,
    h: Inches,
    fill_color: RGBColor = COLOR_CARD_SLATE,
    border_color: RGBColor = COLOR_CARD_BORDER,
    border_width: Pt = Pt(1.0),
    shape_type: MSO_SHAPE = MSO_SHAPE.ROUNDED_RECTANGLE,
):
    """Draws a clean container card with solid fill and 1px border."""
    card = slide.shapes.add_shape(shape_type, x, y, w, h)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = border_width
    else:
        card.line.fill.background()
    return card


def add_takeaway_banner(
    slide,
    points: List[str],
    y: Inches = Inches(8.4),
    h: Inches = Inches(1.55),
    header_text: str = "What this means:",
):
    """
    Renders the signature solid Electric Cyan (#3EC0C0) takeaway banner
    with bold dark navy text (#031E45) across the content width.
    """
    banner = add_card(
        slide=slide,
        x=MARGIN_X,
        y=y,
        w=CONTENT_WIDTH,
        h=h,
        fill_color=COLOR_CYAN,
        border_color=COLOR_CYAN_DEEP,
    )

    tb = slide.shapes.add_textbox(
        MARGIN_X + Inches(0.4), y + Inches(0.15), CONTENT_WIDTH - Inches(0.8), h - Inches(0.3)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_head = tf.paragraphs[0]
    p_head.text = header_text
    p_head.font.name = FONT_PRIMARY
    p_head.font.size = SIZE_CARD_HEADER
    p_head.font.bold = True
    p_head.font.color.rgb = COLOR_DARK_TEXT
    p_head.alignment = PP_ALIGN.CENTER

    for pt in points:
        p = tf.add_paragraph()
        p.text = pt
        p.font.name = FONT_PRIMARY
        p.font.size = SIZE_BODY
        p.font.color.rgb = COLOR_DARK_TEXT
        p.alignment = PP_ALIGN.CENTER

    return banner


def add_stat_card(
    slide,
    x: Inches,
    y: Inches,
    w: Inches,
    h: Inches,
    value: str,
    label: str,
    context: Optional[str] = None,
):
    """Draws a metric card with oversized 64pt Cyan number and white label."""
    card = add_card(slide, x, y, w, h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CARD_BORDER)

    tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), w - Inches(0.4), h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    # Value (64pt Cyan)
    p_v = tf.paragraphs[0]
    p_v.text = value
    p_v.font.name = FONT_PRIMARY
    p_v.font.size = SIZE_HERO_STAT
    p_v.font.bold = True
    p_v.font.color.rgb = COLOR_CYAN
    p_v.alignment = PP_ALIGN.CENTER

    # Label (15pt White)
    p_l = tf.add_paragraph()
    p_l.text = label
    p_l.font.name = FONT_PRIMARY
    p_l.font.size = SIZE_BODY
    p_l.font.color.rgb = COLOR_WHITE
    p_l.alignment = PP_ALIGN.CENTER

    # Context (13pt Muted)
    if context:
        p_c = tf.add_paragraph()
        p_c.text = context
        p_c.font.name = FONT_PRIMARY
        p_c.font.size = SIZE_BODY_SM
        p_c.font.color.rgb = COLOR_MUTED_SLATE
        p_c.alignment = PP_ALIGN.CENTER

    return card


def add_media_placeholder(
    slide,
    x: Inches,
    y: Inches,
    w: Inches,
    h: Inches,
    title: str,
    instructions: str,
):
    """
    Renders an editorial video/screenshot placeholder frame with a play glyph,
    avoiding bloated binary media files while clearly guiding the user.
    """
    card = add_card(slide, x, y, w, h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN_DEEP)

    # Play badge shape in center
    badge_w = Inches(3.2)
    badge_h = Inches(0.7)
    badge_x = x + (w - badge_w) / 2
    badge_y = y + Inches(1.2)
    badge = add_card(slide, badge_x, badge_y, badge_w, badge_h, fill_color=COLOR_NAVY, border_color=COLOR_CYAN)

    tb_b = slide.shapes.add_textbox(badge_x, badge_y + Inches(0.12), badge_w, Inches(0.45))
    tf_b = tb_b.text_frame
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = "▶  VIDEO DEMO"
    p_b.font.name = FONT_PRIMARY
    p_b.font.size = SIZE_CARD_HEADER
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_CYAN
    p_b.alignment = PP_ALIGN.CENTER

    # Title & Instructions
    tb_desc = slide.shapes.add_textbox(x + Inches(0.5), badge_y + Inches(1.0), w - Inches(1.0), Inches(2.0))
    tf_d = tb_desc.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = tf_d.margin_right = tf_d.margin_top = tf_d.margin_bottom = 0

    p_t = tf_d.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_PRIMARY
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    p_t.alignment = PP_ALIGN.CENTER

    p_i = tf_d.add_paragraph()
    p_i.text = instructions
    p_i.font.name = FONT_PRIMARY
    p_i.font.size = SIZE_BODY
    p_i.font.color.rgb = COLOR_MUTED_SLATE
    p_i.alignment = PP_ALIGN.CENTER

    return card
