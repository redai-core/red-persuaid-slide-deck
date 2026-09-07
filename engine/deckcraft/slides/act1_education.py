#!/usr/bin/env python3
"""
PersuAId DeckCraft Act I: The Wake-Up Call (Slides 1 to 5)
1. Cover ("THE NEW BATTLE FOR [ VISIBILITY ]")
2. Confidentiality & Copyright Notice
3. Paradigm Shift ("When AI answers, clicks disappear" SEO vs GEO)
4. Real Search Comparison (10 Blue Links vs AI Overview Box)
5. Ingestion Ecosystem & Live Search Video Placeholder
"""

from typing import Dict, Any
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from engine.deckcraft.tokens import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    MARGIN_X,
    MARGIN_Y,
    CONTENT_WIDTH,
    COLOR_OBSIDIAN,
    COLOR_NAVY,
    COLOR_CYAN,
    COLOR_CARD_SLATE,
    COLOR_CARD_BORDER,
    COLOR_WHITE,
    COLOR_COOL_GRAY,
    COLOR_MUTED_SLATE,

    COLOR_DARK_TEXT,
    FONT_PRIMARY,
    SIZE_COVER_TITLE,
    SIZE_COVER_SUBTITLE,
    SIZE_CARD_HEADER,
    SIZE_BODY,
)
from engine.deckcraft.primitives import (
    set_slide_background,
    add_header,
    add_footer,
    add_card,
    add_takeaway_banner,
    add_media_placeholder,
)


def build_slide_01_cover(slide, data: Dict[str, Any]):
    """Slide 1: Executive Cover Slide with Stylized Search Bar."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    # Top brand header
    tb_top = slide.shapes.add_textbox(MARGIN_X, MARGIN_Y, CONTENT_WIDTH, Inches(1.0))
    tf_top = tb_top.text_frame
    tf_top.margin_left = tf_top.margin_right = tf_top.margin_top = tf_top.margin_bottom = 0
    p_logo = tf_top.paragraphs[0]
    p_logo.text = "red comm"
    p_logo.font.name = FONT_PRIMARY
    p_logo.font.size = Pt(20)
    p_logo.font.bold = True
    p_logo.font.color.rgb = COLOR_WHITE

    # Client Brand Badge
    badge_y = Inches(3.2)
    tb_b = slide.shapes.add_textbox(MARGIN_X, badge_y, Inches(6.0), Inches(0.8))
    tf_b = tb_b.text_frame
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = f"{brand.lower()}  |  GEO AUDIT"
    p_b.font.name = FONT_PRIMARY
    p_b.font.size = Pt(26)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_CYAN

    # Main Bold Display Title
    title_y = Inches(4.2)
    tb_title = slide.shapes.add_textbox(MARGIN_X, title_y, Inches(12.0), Inches(1.4))
    tf_t = tb_title.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = "THE NEW BATTLE"
    p_t.font.name = FONT_PRIMARY
    p_t.font.size = SIZE_COVER_TITLE
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

    # Search Bar Graphic Container
    search_y = Inches(5.6)
    search_w = Inches(10.5)
    search_h = Inches(1.4)
    add_card(slide, MARGIN_X, search_y, search_w, search_h, fill_color=COLOR_OBSIDIAN, border_color=COLOR_WHITE, border_width=Pt(2.0))

    tb_s = slide.shapes.add_textbox(MARGIN_X + Inches(0.4), search_y + Inches(0.3), search_w - Inches(0.8), Inches(0.8))
    tf_s = tb_s.text_frame
    tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = "FOR VISIBILITY   |  AI Search"
    p_s.font.name = FONT_PRIMARY
    p_s.font.size = Pt(44)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_WHITE


    # Subtitle
    sub_y = Inches(7.4)
    tb_sub = slide.shapes.add_textbox(MARGIN_X, sub_y, Inches(14.0), Inches(1.0))
    tf_sub = tb_sub.text_frame
    tf_sub.word_wrap = True
    tf_sub.margin_left = tf_sub.margin_right = tf_sub.margin_top = tf_sub.margin_bottom = 0
    p_sub1 = tf_sub.paragraphs[0]
    p_sub1.text = "GEO + SEO: How Your Brand Gets Found and"
    p_sub1.font.name = FONT_PRIMARY
    p_sub1.font.size = SIZE_COVER_SUBTITLE
    p_sub1.font.bold = True
    p_sub1.font.color.rgb = COLOR_WHITE

    p_sub2 = tf_sub.add_paragraph()
    p_sub2.text = "Recommended by AI"
    p_sub2.font.name = FONT_PRIMARY
    p_sub2.font.size = SIZE_COVER_SUBTITLE
    p_sub2.font.bold = True
    p_sub2.font.color.rgb = COLOR_WHITE

    add_footer(slide, brand)


def build_slide_02_legal(slide, data: Dict[str, Any]):
    """Slide 2: Confidentiality and Legal Disclaimer."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    box = slide.shapes.add_textbox(MARGIN_X + Inches(2.0), Inches(4.2), CONTENT_WIDTH - Inches(4.0), Inches(3.0))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p1 = tf.paragraphs[0]
    p1.text = "© 2026 REDCOMM. All rights reserved."
    p1.font.name = FONT_PRIMARY
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE

    p2 = tf.add_paragraph()
    p2.text = (
        "\nThis presentation and its contents are confidential and intended solely for the recipient. "
        "No part may be reproduced, distributed, or disclosed without prior written permission of Redcomm Indonesia.\n\n"
        f"Prepared specifically for {brand} executive leadership."
    )
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLOR_MUTED_SLATE

    add_footer(slide, brand)


def build_slide_03_shift(slide, data: Dict[str, Any]):
    """Slide 3: Paradigm Shift: SEO Only vs SEO + GEO."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="THE WORLD YOUR AUDIENCE LIVES IN NOW",
        title="When AI answers, clicks disappear",
        subtitle=None,
    )

    card_w = Inches(8.3)
    card_h = Inches(6.0)
    card_y = Inches(2.8)

    # Left Card: SEO Only
    add_card(slide, MARGIN_X, card_y, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)
    tb_l = slide.shapes.add_textbox(MARGIN_X + Inches(0.8), card_y + Inches(0.6), card_w - Inches(1.6), card_h - Inches(1.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = 0

    p_lh = tf_l.paragraphs[0]
    p_lh.text = "SEO Only"
    p_lh.font.name = FONT_PRIMARY
    p_lh.font.size = Pt(28)
    p_lh.font.bold = True
    p_lh.font.color.rgb = COLOR_WHITE
    p_lh.alignment = PP_ALIGN.CENTER

    seo_bullets = [
        "→ User searches on Google",
        "→ 10 blue links appear",
        "→ User clicks → visits website",
        "→ Brand wins through ranking",
        "→ Success = Page 1 position",
    ]
    for b in seo_bullets:
        p = tf_l.add_paragraph()
        p.text = f"\n{b}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(17)
        p.font.color.rgb = COLOR_COOL_GRAY

    # Center "NOW" badge
    now_x = MARGIN_X + card_w + Inches(0.2)
    now_box = slide.shapes.add_textbox(now_x, card_y + Inches(2.6), Inches(0.8), Inches(0.8))
    tf_now = now_box.text_frame
    tf_now.margin_left = tf_now.margin_right = tf_now.margin_top = tf_now.margin_bottom = 0
    p_now = tf_now.paragraphs[0]
    p_now.text = "NOW"
    p_now.font.name = FONT_PRIMARY
    p_now.font.size = Pt(16)
    p_now.font.bold = True
    p_now.font.color.rgb = COLOR_CYAN
    p_now.alignment = PP_ALIGN.CENTER

    # Right Card: SEO + GEO
    right_x = MARGIN_X + card_w + Inches(1.2)
    add_card(slide, right_x, card_y, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)
    tb_r = slide.shapes.add_textbox(right_x + Inches(0.8), card_y + Inches(0.6), card_w - Inches(1.6), card_h - Inches(1.2))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0

    p_rh = tf_r.paragraphs[0]
    p_rh.text = "SEO + GEO"
    p_rh.font.name = FONT_PRIMARY
    p_rh.font.size = Pt(28)
    p_rh.font.bold = True
    p_rh.font.color.rgb = COLOR_CYAN
    p_rh.alignment = PP_ALIGN.CENTER

    p_sub = tf_r.add_paragraph()
    p_sub.text = "Two disciplines. One goal: your brand gets found."
    p_sub.font.name = FONT_PRIMARY
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_MUTED_SLATE
    p_sub.alignment = PP_ALIGN.CENTER

    geo_bullets = [
        "✓ User asks ChatGPT, Gemini, Perplexity",
        "✓ AI gives ONE direct answer",
        "✓ No click needed — decision made",
        "✓ Brand wins through AI citation",
        "✓ Success = Being the AI's answer",
    ]
    for b in geo_bullets:
        p = tf_r.add_paragraph()
        p.text = f"\n{b}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(17)
        p.font.color.rgb = COLOR_WHITE

    add_footer(slide, brand)


def build_slide_04_comparison(slide, data: Dict[str, Any]):
    """Slide 4: Real-World Search Visual Comparison + Bottom Teal Banner."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")
    category = data.get("category", "your category")

    add_header(
        slide=slide,
        kicker="THE DIRECT SEARCH COMPARISON",
        title="From 10 blue links to a single synthesized verdict",
        subtitle=f"Query: 'Bagaimana memilih {category} yang tepat?'",
    )

    card_w = Inches(8.5)
    card_h = Inches(4.8)
    card_y = Inches(2.6)

    # Left: Traditional SERP Box
    add_card(slide, MARGIN_X, card_y, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CARD_BORDER)
    tb_l = slide.shapes.add_textbox(MARGIN_X + Inches(0.5), card_y + Inches(0.4), card_w - Inches(1.0), card_h - Inches(0.8))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = 0

    p_lh = tf_l.paragraphs[0]
    p_lh.text = "Google Traditional Search (SEO)"
    p_lh.font.name = FONT_PRIMARY
    p_lh.font.size = Pt(20)
    p_lh.font.bold = True
    p_lh.font.color.rgb = COLOR_WHITE

    p_lb = tf_l.add_paragraph()
    p_lb.text = (
        "\n• Multiple competing sponsored ads at top\n"
        "• 10 scattered blue links requiring user research\n"
        "• Click-through drop-off at every stage\n"
        "• Winner is whoever buys ads or optimizes keywords"
    )
    p_lb.font.name = FONT_PRIMARY
    p_lb.font.size = Pt(15)
    p_lb.font.color.rgb = COLOR_MUTED_SLATE

    # Right: AI Overview Box
    right_x = MARGIN_X + card_w + Inches(0.8)
    add_card(slide, right_x, card_y, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)
    tb_r = slide.shapes.add_textbox(right_x + Inches(0.5), card_y + Inches(0.4), card_w - Inches(1.0), card_h - Inches(0.8))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0

    p_rh = tf_r.paragraphs[0]
    p_rh.text = "Google AI Overview & ChatGPT (GEO)"
    p_rh.font.name = FONT_PRIMARY
    p_rh.font.size = Pt(20)
    p_rh.font.bold = True
    p_rh.font.color.rgb = COLOR_CYAN

    p_rb = tf_r.add_paragraph()
    p_rb.text = (
        "\n• AI generates ONE immediate, synthesized answer\n"
        "• Cites only 2–3 authority sources directly\n"
        "�� User accepts recommendation without visiting websites\n"
        "• Winner is whoever the LLM trusts as the category authority"
    )
    p_rb.font.name = FONT_PRIMARY
    p_rb.font.size = Pt(15)
    p_rb.font.color.rgb = COLOR_WHITE

    # Bottom Full-Width Signature Banner
    add_takeaway_banner(
        slide=slide,
        points=["SEO helps your brand get found. GEO helps your brand get chosen."],
        y=Inches(8.0),
        h=Inches(1.5),
        header_text="THE STRATEGIC IMPERATIVE:",
    )

    add_footer(slide, brand)


def build_slide_05_ecosystem(slide, data: Dict[str, Any]):
    """Slide 5: Understanding the LLM Engine + Live Search Video Demo Placeholder."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="HOW AI DECIDES WHAT TO RECOMMEND",
        title="Understanding the LLM Engine",
        subtitle="The brand most consistently cited across authority sources becomes the brand AI recommends.",
    )

    # Left: Search Journey Video Demo Placeholder
    add_media_placeholder(
        slide=slide,
        x=MARGIN_X,
        y=Inches(2.6),
        w=Inches(9.5),
        h=Inches(5.4),
        title="Live LLM Interaction Demo",
        instructions="Insert 10–15s screen recording of ChatGPT or Perplexity answering a prompt in real-time.",
    )

    # Right: Engine Dominance Share Breakdown
    right_x = MARGIN_X + Inches(10.0)
    add_card(slide, right_x, Inches(2.6), Inches(7.8), Inches(5.4), fill_color=COLOR_CARD_SLATE, border_color=COLOR_CARD_BORDER)

    tb = slide.shapes.add_textbox(right_x + Inches(0.6), Inches(3.0), Inches(6.6), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_h = tf.paragraphs[0]
    p_h.text = "Dominance of Chat-Based AI"
    p_h.font.name = FONT_PRIMARY
    p_h.font.size = Pt(22)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_WHITE

    p_sub = tf.add_paragraph()
    p_sub.text = "Survey data consistently shows chat models dominate AI discovery:"
    p_sub.font.name = FONT_PRIMARY
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_MUTED_SLATE

    stats = [
        ("ChatGPT", "83.5%", "Most widely used standalone AI engine"),
        ("Perplexity", "10.3%", "Rapidly growing research platform"),
        ("Google Gemini", "3.3%", "Embedded in Android and Google Search"),
        ("Claude", "2.2%", "Technical and long-form analysis"),
        ("Microsoft Copilot", "0.6%", "Enterprise desktop distribution"),
    ]
    for eng, pct, note in stats:
        p = tf.add_paragraph()
        p.text = f"\n• {eng} ({pct}): {note}"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_COOL_GRAY

    # Bottom Takeaway Card
    add_takeaway_banner(
        slide=slide,
        points=["The brand most consistently cited becomes the brand AI recommends."],
        y=Inches(8.4),
        h=Inches(1.5),
    )

    add_footer(slide, brand)
