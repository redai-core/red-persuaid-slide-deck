#!/usr/bin/env python3
"""
PersuAId DeckCraft Act IV: The Retainer SOW & Close (Slides 16 to 21)
16. Measurement KPIs (Baseline -> Target Milestones)
17. Section Divider: APPENDIX
18. Proof Points & Case Studies (+77.8% Visibility Gain)
19. Proprietary GEO Software Platform Demo & Video Placeholder
20. Recommended Monthly Retainer & SOW (25M–35M IDR + Squad Scope)
21. Closer: "YOUR BRAND DESERVES To Be the Answer"
"""

from typing import Dict, Any
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from engine.deckcraft.tokens import (
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    MARGIN_X,
    MARGIN_Y,
    CONTENT_WIDTH,
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
    SIZE_COVER_TITLE,
    SIZE_SECTION_TITLE,
    SIZE_HERO_STAT,
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


def build_slide_16_measurement(slide, data: Dict[str, Any]):
    """Slide 16: Measurement: How we know it's working — the metrics that matter."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="MEASUREMENT",
        title="How we know it's working — the metrics that matter",
        subtitle=None,
    )

    card_w = (CONTENT_WIDTH - Inches(0.8)) / 3
    card_h = Inches(4.8)
    card_y = Inches(2.6)

    kpis = [
        ("AI Mention Rate", "9.3%", "16%+", f"Count {brand} mentions across standard prompts"),
        ("AI Answer Position", "#4.1 avg", "#3 avg", "Average rank when client appears in multi-brand answers"),
        ("Official Citations", "4.1%", "8.2%+", "% of AI responses that cite official domain as a source"),
    ]

    for i, (title, base, target, desc) in enumerate(kpis):
        cx = MARGIN_X + (i * (card_w + Inches(0.4)))
        add_card(slide, cx, card_y, card_w, card_h, fill_color=COLOR_WHITE, border_color=None)

        tb = slide.shapes.add_textbox(cx + Inches(0.5), card_y + Inches(0.6), card_w - Inches(1.0), card_h - Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_PRIMARY
        p_t.font.size = Pt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_DARK_TEXT
        p_t.alignment = PP_ALIGN.CENTER

        # Milestone Numbers
        p_m = tf.add_paragraph()
        p_m.text = f"\n{base}  →  {target}"
        p_m.font.name = FONT_PRIMARY
        p_m.font.size = Pt(32)
        p_m.font.bold = True
        p_m.font.color.rgb = COLOR_CYAN_DEEP
        p_m.alignment = PP_ALIGN.CENTER

        # Description
        p_d = tf.add_paragraph()
        p_d.text = f"\n{desc}"
        p_d.font.name = FONT_PRIMARY
        p_d.font.size = Pt(14)
        p_d.font.color.rgb = COLOR_DARK_TEXT
        p_d.alignment = PP_ALIGN.CENTER

    add_takeaway_banner(
        slide=slide,
        points=["Target metrics reflect realistic, achievable gains over a 6-month structured engagement."],
        y=Inches(8.0),
        h=Inches(1.5),
        header_text="MEASUREMENT FRAMEWORK:",
    )

    add_footer(slide, brand)


def build_slide_17_divider_appendix(slide, data: Dict[str, Any]):
    """Slide 17: Section Divider: APPENDIX."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    box = slide.shapes.add_textbox(MARGIN_X, Inches(4.5), CONTENT_WIDTH, Inches(2.5))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_k = tf.paragraphs[0]
    p_k.text = "SUPPORTING INTELLIGENCE"
    p_k.font.name = FONT_PRIMARY
    p_k.font.size = Pt(16)
    p_k.font.bold = True
    p_k.font.color.rgb = COLOR_CYAN
    p_k.alignment = PP_ALIGN.CENTER

    p_t = tf.add_paragraph()
    p_t.text = "APPENDIX"
    p_t.font.name = FONT_PRIMARY
    p_t.font.size = SIZE_SECTION_TITLE
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    p_t.alignment = PP_ALIGN.CENTER

    p_s = tf.add_paragraph()
    p_s.text = "Case studies, proprietary tools, and commercial engagement structures"
    p_s.font.name = FONT_PRIMARY
    p_s.font.size = Pt(18)
    p_s.font.color.rgb = COLOR_MUTED_SLATE
    p_s.alignment = PP_ALIGN.CENTER

    add_footer(slide, brand)


def build_slide_18_case_studies(slide, data: Dict[str, Any]):
    """Slide 18: Client Proof Points & Case Studies (+77.8% Visibility Gain)."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="PROVEN TRACK RECORD",
        title="Measurable visibility growth across local market leaders",
        subtitle=None,
    )

    card_w = (CONTENT_WIDTH - Inches(0.6)) / 2
    card_h = Inches(4.8)
    card_y = Inches(2.6)

    # Left Case: Kavacare Healthcare
    add_card(slide, MARGIN_X, card_y, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)
    tb_c1 = slide.shapes.add_textbox(MARGIN_X + Inches(0.6), card_y + Inches(0.6), card_w - Inches(1.2), card_h - Inches(1.2))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_right = tf_c1.margin_top = tf_c1.margin_bottom = 0

    p1_t = tf_c1.paragraphs[0]
    p1_t.text = "Healthcare Network Case Study"
    p1_t.font.name = FONT_PRIMARY
    p1_t.font.size = Pt(22)
    p1_t.font.bold = True
    p1_t.font.color.rgb = COLOR_WHITE

    p1_v = tf_c1.add_paragraph()
    p1_v.text = "\n+77.8%  Visibility Gain"
    p1_v.font.name = FONT_PRIMARY
    p1_v.font.size = Pt(30)
    p1_v.font.bold = True
    p1_v.font.color.rgb = COLOR_CYAN

    p1_d = tf_c1.add_paragraph()
    p1_d.text = (
        "\n• Redefined clinical editorial structure across 120 key prompts\n"
        "• Established dominant citation share on home care and specialist queries\n"
        "• Shifted brand from unranked to #1 recommended network on ChatGPT"
    )
    p1_d.font.name = FONT_PRIMARY
    p1_d.font.size = Pt(15)
    p1_d.font.color.rgb = COLOR_COOL_GRAY

    # Right Case: Consumer / Enterprise Brand
    right_x = MARGIN_X + card_w + Inches(0.6)
    add_card(slide, right_x, card_y, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CARD_BORDER)
    tb_c2 = slide.shapes.add_textbox(right_x + Inches(0.6), card_y + Inches(0.6), card_w - Inches(1.2), card_h - Inches(1.2))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_right = tf_c2.margin_top = tf_c2.margin_bottom = 0

    p2_t = tf_c2.paragraphs[0]
    p2_t.text = "Consumer Manufacturing Case Study"
    p2_t.font.name = FONT_PRIMARY
    p2_t.font.size = Pt(22)
    p2_t.font.bold = True
    p2_t.font.color.rgb = COLOR_WHITE

    p2_v = tf_c2.add_paragraph()
    p2_v.text = "\n3.4x  Citation Volume"
    p2_v.font.name = FONT_PRIMARY
    p2_v.font.size = Pt(30)
    p2_v.font.bold = True
    p2_v.font.color.rgb = COLOR_WHITE

    p2_d = tf_c2.add_paragraph()
    p2_d.text = (
        "\n• Deployed comprehensive technical schema and product knowledge graph\n"
        "• Replaced third-party reseller blogs with direct brand citations\n"
        "• Overcame established legacy incumbents in AI Overviews"
    )
    p2_d.font.name = FONT_PRIMARY
    p2_d.font.size = Pt(15)
    p2_d.font.color.rgb = COLOR_COOL_GRAY

    add_takeaway_banner(
        slide=slide,
        points=["Structured editorial and technical GEO consistently lifts AI recommendations within 60–90 days."],
        y=Inches(8.0),
        h=Inches(1.5),
        header_text="VERIFIED IMPACT:",
    )

    add_footer(slide, brand)


def build_slide_19_geo_tools_demo(slide, data: Dict[str, Any]):
    """Slide 19: Proprietary GEO Software Tools & Platform Video Demo Placeholder."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="OUR OWN GEO TOOLS - INFLUENCING LLM",
        title="PersuAId Platform Intelligence",
        subtitle=None,
    )

    # Left: Platform UI Video Placeholder
    add_media_placeholder(
        slide=slide,
        x=MARGIN_X,
        y=Inches(2.6),
        w=Inches(9.5),
        h=Inches(6.8),
        title="PersuAId Dashboard Demo",
        instructions="Insert 10–15s screen recording demonstrating real-time authority score, press tracking, and AI citation monitoring.",
    )

    # Right: 3 Value Proposition Cards
    right_x = MARGIN_X + Inches(10.0)
    card_w = Inches(7.8)
    card_h = Inches(1.8)

    props = [
        ("AI-Powered GEO Platform", "Maximizing brand visibility, authority signals, and citability across all major generative models."),
        ("Bridges Search & AI", "Connects high-performing search engine optimization with generative engine ranking signals."),
        ("Actionable & Measurable", "Provides weekly diagnostic crawls, bot log verification, and prompt gap remediation."),
    ]
    for i, (p_title, p_desc) in enumerate(props):
        cy = Inches(2.6) + (i * Inches(2.1))
        add_card(slide, right_x, cy, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)

        tb = slide.shapes.add_textbox(right_x + Inches(0.5), cy + Inches(0.25), card_w - Inches(1.0), card_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p_h = tf.paragraphs[0]
        p_h.text = p_title
        p_h.font.name = FONT_PRIMARY
        p_h.font.size = Pt(17)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE

        p_b = tf.add_paragraph()
        p_b.text = p_desc
        p_b.font.name = FONT_PRIMARY
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = COLOR_MUTED_SLATE

    # DEMO Badge at bottom-right
    add_card(slide, right_x + Inches(2.2), Inches(9.0), Inches(3.4), Inches(0.7), fill_color=COLOR_NAVY, border_color=COLOR_CYAN)
    tb_demo = slide.shapes.add_textbox(right_x + Inches(2.2), Inches(9.12), Inches(3.4), Inches(0.45))
    tf_demo = tb_demo.text_frame
    tf_demo.margin_left = tf_demo.margin_right = tf_demo.margin_top = tf_demo.margin_bottom = 0
    p_dm = tf_demo.paragraphs[0]
    p_dm.text = "LIVE PLATFORM DEMO"
    p_dm.font.name = FONT_PRIMARY
    p_dm.font.size = Pt(15)
    p_dm.font.bold = True
    p_dm.font.color.rgb = COLOR_CYAN
    p_dm.alignment = PP_ALIGN.CENTER

    add_footer(slide, brand)


def build_slide_20_retainer_sow(slide, data: Dict[str, Any]):
    """Slide 20: Recommended Monthly Retainer & Scope of Work."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="OUR PLANS",
        title="Recommended Monthly Retainer",
        subtitle=None,
    )

    top_y = Inches(2.4)
    top_h = Inches(4.5)

    # Box 1: On-page deliverables
    b1_w = Inches(5.6)
    add_card(slide, MARGIN_X, top_y, b1_w, top_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)
    tb1 = slide.shapes.add_textbox(MARGIN_X + Inches(0.4), top_y + Inches(0.4), b1_w - Inches(0.8), top_h - Inches(0.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = tf1.margin_top = tf1.margin_bottom = 0

    p1_h = tf1.paragraphs[0]
    p1_h.text = "Content & On-Page Optimization"
    p1_h.font.name = FONT_PRIMARY
    p1_h.font.size = Pt(17)
    p1_h.font.bold = True
    p1_h.font.color.rgb = COLOR_CYAN

    p1_b = tf1.add_paragraph()
    p1_b.text = (
        "\n✓ 60 category-written pieces\n"
        f"✓ {brand.lower()}.com optimization & schema\n"
        "✓ AI-prompt-aligned content structure\n"
        "✓ Article content editorial review\n"
        "✓ Monthly performance report\n"
        "✓ 6-month minimum commitment"
    )
    p1_b.font.name = FONT_PRIMARY
    p1_b.font.size = Pt(14)
    p1_b.font.color.rgb = COLOR_WHITE

    # Box 2: Off-page & Citation Outreach
    b2_x = MARGIN_X + b1_w + Inches(0.4)
    b2_w = Inches(5.6)
    add_card(slide, b2_x, top_y, b2_w, top_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)
    tb2 = slide.shapes.add_textbox(b2_x + Inches(0.4), top_y + Inches(0.4), b2_w - Inches(0.8), top_h - Inches(0.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_right = tf2.margin_top = tf2.margin_bottom = 0

    p2_h = tf2.paragraphs[0]
    p2_h.text = "Third-Party Citation & Off-Page"
    p2_h.font.name = FONT_PRIMARY
    p2_h.font.size = Pt(17)
    p2_h.font.bold = True
    p2_h.font.color.rgb = COLOR_CYAN

    p2_b = tf2.add_paragraph()
    p2_b.text = (
        "\n✓ Top publisher recommendation outreach\n"
        "✓ 10 high-DA authority articles\n"
        "✓ Wikipedia & Wikidata presence\n"
        "✓ Community forum thread placement\n"
        "✓ AI social content alignment\n"
        "✓ Monthly citation tracking"
    )
    p2_b.font.name = FONT_PRIMARY
    p2_b.font.size = Pt(14)
    p2_b.font.color.rgb = COLOR_WHITE

    # Box 3: Commercial Pricing Box
    b3_x = b2_x + b2_w + Inches(0.4)
    b3_w = Inches(5.8)
    add_card(slide, b3_x, top_y, b3_w, top_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)
    tb3 = slide.shapes.add_textbox(b3_x + Inches(0.4), top_y + Inches(0.4), b3_w - Inches(0.8), top_h - Inches(0.8))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_right = tf3.margin_top = tf3.margin_bottom = 0

    p3_s = tf3.paragraphs[0]
    p3_s.text = "~35 mio~"
    p3_s.font.name = FONT_PRIMARY
    p3_s.font.size = Pt(22)
    p3_s.font.color.rgb = COLOR_MUTED_SLATE
    p3_s.alignment = PP_ALIGN.CENTER

    p3_p = tf3.add_paragraph()
    p3_p.text = "25 mio"
    p3_p.font.name = FONT_PRIMARY
    p3_p.font.size = Pt(54)
    p3_p.font.bold = True
    p3_p.font.color.rgb = COLOR_CYAN
    p3_p.alignment = PP_ALIGN.CENTER

    p3_m = tf3.add_paragraph()
    p3_m.text = "/month\n"
    p3_m.font.name = FONT_PRIMARY
    p3_m.font.size = Pt(20)
    p3_m.font.bold = True
    p3_m.font.color.rgb = COLOR_WHITE
    p3_m.alignment = PP_ALIGN.CENTER

    p3_n = tf3.add_paragraph()
    p3_n.text = "Retainer fee for SEO/GEO management.\nMinimum 6 months engagement.\n*Excludes third-party tool fees."
    p3_n.font.name = FONT_PRIMARY
    p3_n.font.size = Pt(13)
    p3_n.font.color.rgb = COLOR_MUTED_SLATE
    p3_n.alignment = PP_ALIGN.CENTER

    # Bottom Squad Container
    squad_y = Inches(7.3)
    squad_h = Inches(2.2)
    add_card(slide, MARGIN_X, squad_y, CONTENT_WIDTH, squad_h, fill_color=COLOR_NAVY, border_color=COLOR_CYAN)
    tb_sq = slide.shapes.add_textbox(MARGIN_X + Inches(0.6), squad_y + Inches(0.3), CONTENT_WIDTH - Inches(1.2), squad_h - Inches(0.6))
    tf_sq = tb_sq.text_frame
    tf_sq.word_wrap = True
    tf_sq.margin_left = tf_sq.margin_right = tf_sq.margin_top = tf_sq.margin_bottom = 0

    p_sqh = tf_sq.paragraphs[0]
    p_sqh.text = "Dedicated SEO / GEO Squad Allocation"
    p_sqh.font.name = FONT_PRIMARY
    p_sqh.font.size = Pt(18)
    p_sqh.font.bold = True
    p_sqh.font.color.rgb = COLOR_CYAN

    p_sqb = tf_sq.add_paragraph()
    p_sqb.text = (
        "\n• SEO/GEO Strategist — Strategy, roadmap & performance optimization    "
        "• Technical SEO Team — On-page optimization & structured data\n"
        "• Prompt Researcher — AI query mapping & consumer intent research       "
        "• Community Engagement — Publisher outreach, forums & citations\n"
        "• Content Writer — AI-ready articles & editorial content               "
        "• Account Executive — Project management & monthly reporting"
    )
    p_sqb.font.name = FONT_PRIMARY
    p_sqb.font.size = Pt(13)
    p_sqb.font.color.rgb = COLOR_WHITE

    add_footer(slide, brand)


def build_slide_21_closer(slide, data: Dict[str, Any]):
    """Slide 21: Closing Call to Action: YOUR BRAND DESERVES To Be the Answer."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    box = slide.shapes.add_textbox(MARGIN_X + Inches(1.0), Inches(3.2), CONTENT_WIDTH - Inches(2.0), Inches(4.5))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_tag = tf.paragraphs[0]
    p_tag.text = "YOUR BRAND DESERVES"
    p_tag.font.name = FONT_PRIMARY
    p_tag.font.size = Pt(28)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_WHITE
    p_tag.alignment = PP_ALIGN.CENTER

    p_ans = tf.add_paragraph()
    p_ans.text = "To Be the Answer"
    p_ans.font.name = FONT_PRIMARY
    p_ans.font.size = Pt(64)
    p_ans.font.bold = True
    p_ans.font.color.rgb = COLOR_WHITE
    p_ans.alignment = PP_ALIGN.CENTER

    p_cta = tf.add_paragraph()
    p_cta.text = f"\nLet's run a complete brand audit for {data.get('category', 'your category')}."
    p_cta.font.name = FONT_PRIMARY
    p_cta.font.size = Pt(26)
    p_cta.font.bold = True
    p_cta.font.color.rgb = COLOR_CYAN
    p_cta.alignment = PP_ALIGN.CENTER

    add_footer(slide, brand)
