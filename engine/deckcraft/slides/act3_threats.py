#!/usr/bin/env python3
"""
PersuAId DeckCraft Act III: The Strategic Threat & Mechanism (Slides 12 to 15)
12. Competitor Landscape Matrix (How each brand is framed by AI)
13. The Asset You Already Hold (Owned differentiators vs blind spots)
14. The Source Base (Citations Matrix Table & Lever Badges)
15. Underneath Both Workstreams (Always-On Category Intelligence)
"""

from typing import Dict, Any, List
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
    SIZE_CARD_HEADER,
    SIZE_BODY,
    SIZE_BODY_SM,
)
from engine.deckcraft.primitives import (
    set_slide_background,
    add_header,
    add_footer,
    add_card,
    add_stat_card,
    add_takeaway_banner,
)


def build_slide_12_competitor_matrix(slide, data: Dict[str, Any]):
    """Slide 12: Competitor Landscape Matrix: Stacked Rows with Client Highlighted."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="COMPETITOR LANDSCAPE",
        title=f"How each brand is framed by AI — and where {brand} fits",
        subtitle=None,
    )

    rows = [
        ("Competitor A", "Premium performance", "31.2%", "Ranked #1 for 'best category product'; associated with high performance and design.", "Strong editorial presence on top review portals and YouTube."),
        ("Competitor B", "Budget leader", "28.4%", "Positioned as affordable high-volume leader; dominates price and discount queries.", "Dominates budget queries; heavy Reddit and community presence."),
        ("Competitor C", "Trusted local legacy", "24.7%", "Consumer electronics brand halo effect; positioned as reliable and durable.", "Legacy brand trust; dominates branded search queries across all 3 engines."),
        ("Competitor D", "Global new entrant", "19.1%", "Entering market with global scale and massive PR budget.", "Massive PR budget; international tech authority coverage."),
        (brand, "Enterprise / Infrastructure", "9.3%", "Strong operational depth and scale; cited mostly in B2B/fleet context, not consumer purchase.", "Unique infrastructure depth; story not yet published in consumer lifestyle media."),
    ]

    start_y = Inches(2.3)
    row_h = Inches(1.3)
    spacing = Inches(0.15)

    for i, (b_name, tag, sov, framing, driver) in enumerate(rows):
        is_client = (b_name.lower() == brand.lower())
        y = start_y + (i * (row_h + spacing))

        card_fill = COLOR_CARD_SLATE if not is_client else COLOR_NAVY
        border_col = COLOR_CARD_BORDER if not is_client else COLOR_CYAN
        add_card(slide, MARGIN_X, y, CONTENT_WIDTH, row_h, fill_color=card_fill, border_color=border_col)

        # Brand Tag Pill (Left)
        pill_w = Inches(2.6)
        add_card(slide, MARGIN_X + Inches(0.2), y + Inches(0.2), pill_w, row_h - Inches(0.4), fill_color=COLOR_CYAN if is_client else COLOR_WHITE, border_color=None)
        tb_p = slide.shapes.add_textbox(MARGIN_X + Inches(0.3), y + Inches(0.3), pill_w - Inches(0.2), row_h - Inches(0.6))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
        p_pn = tf_p.paragraphs[0]
        p_pn.text = b_name
        p_pn.font.name = FONT_PRIMARY
        p_pn.font.size = Pt(16)
        p_pn.font.bold = True
        p_pn.font.color.rgb = COLOR_DARK_TEXT
        p_pt = tf_p.add_paragraph()
        p_pt.text = tag
        p_pt.font.name = FONT_PRIMARY
        p_pt.font.size = Pt(11)
        p_pt.font.color.rgb = COLOR_DARK_TEXT

        # SoV %
        tb_sov = slide.shapes.add_textbox(MARGIN_X + Inches(3.0), y + Inches(0.4), Inches(1.4), Inches(0.5))
        tf_sov = tb_sov.text_frame
        tf_sov.margin_left = tf_sov.margin_right = tf_sov.margin_top = tf_sov.margin_bottom = 0
        p_sv = tf_sov.paragraphs[0]
        p_sv.text = sov
        p_sv.font.name = FONT_PRIMARY
        p_sv.font.size = Pt(20)
        p_sv.font.bold = True
        p_sv.font.color.rgb = COLOR_CYAN if is_client else COLOR_WHITE

        # Column 1: AI Framing
        tb_f = slide.shapes.add_textbox(MARGIN_X + Inches(4.6), y + Inches(0.25), Inches(6.4), row_h - Inches(0.5))
        tf_f = tb_f.text_frame
        tf_f.word_wrap = True
        tf_f.margin_left = tf_f.margin_right = tf_f.margin_top = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = framing
        p_f.font.name = FONT_PRIMARY
        p_f.font.size = Pt(13)
        p_f.font.color.rgb = COLOR_CYAN if is_client else COLOR_WHITE

        # Column 2: Content Driver
        tb_d = slide.shapes.add_textbox(MARGIN_X + Inches(11.4), y + Inches(0.25), Inches(6.0), row_h - Inches(0.5))
        tf_d = tb_d.text_frame
        tf_d.word_wrap = True
        tf_d.margin_left = tf_d.margin_right = tf_d.margin_top = tf_d.margin_bottom = 0
        p_d = tf_d.paragraphs[0]
        p_d.text = driver
        p_d.font.name = FONT_PRIMARY
        p_d.font.size = Pt(13)
        p_d.font.color.rgb = COLOR_CYAN if is_client else COLOR_MUTED_SLATE

    add_footer(slide, brand)


def build_slide_13_owned_assets(slide, data: Dict[str, Any]):
    """Slide 13: The Asset You Already Hold: Core Differentiators vs Blind Spots."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="THE ASSET YOU ALREADY HOLD",
        title=f"When AI does name {brand}, it frames it as infrastructure-first",
        subtitle=None,
    )

    card_w = (CONTENT_WIDTH - Inches(0.9)) / 4
    card_h = Inches(2.2)
    card_y = Inches(2.4)

    # 4 Stat Cards
    stats = [
        ("18%", "of mentions place client #1", "On niche queries specifically"),
        ("42%", "of mentions are in top-3", "When core features are queried"),
        ("3.8", "average position when named", "Across multi-brand responses"),
        ("63/100", "average sentiment score", "Neutral-positive baseline"),
    ]
    for i, (val, lbl, ctx) in enumerate(stats):
        x = MARGIN_X + (i * (card_w + Inches(0.3)))
        add_stat_card(slide, x, card_y, card_w, card_h, val, lbl, ctx)

    # Middle Observation
    obs_y = Inches(4.9)
    obs_h = Inches(1.8)
    add_card(slide, MARGIN_X, obs_y, CONTENT_WIDTH, obs_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CARD_BORDER)

    tb_obs = slide.shapes.add_textbox(MARGIN_X + Inches(0.6), obs_y + Inches(0.3), CONTENT_WIDTH - Inches(1.2), obs_h - Inches(0.6))
    tf_obs = tb_obs.text_frame
    tf_obs.word_wrap = True
    tf_obs.margin_left = tf_obs.margin_right = tf_obs.margin_top = tf_obs.margin_bottom = 0

    p1 = tf_obs.paragraphs[0]
    p1.text = f"{brand} appears in only 9.3% of category queries."
    p1.font.name = FONT_PRIMARY
    p1.font.size = Pt(18)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf_obs.add_paragraph()
    p2.text = f"\nWhen it does, AI consistently recognizes it as an infrastructure leader.\nThe gap is that {brand} rarely appears in broader consumer purchase-decision queries."
    p2.font.name = FONT_PRIMARY
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLOR_COOL_GRAY
    p2.alignment = PP_ALIGN.CENTER

    # 3 Owned Asset Pillars
    pillar_y = Inches(7.0)
    pillar_w = (CONTENT_WIDTH - Inches(0.6)) / 3
    pillar_h = Inches(2.4)

    pillars = [
        ("Proprietary Infrastructure", "Largest operational network and service footprint in the region."),
        ("Institutional Trust", "Backing by reputable corporate groups gives strong reliability signals."),
        ("Proven Scale Story", "Millions of operational hours and user transactions validate reliability."),
    ]
    for i, (p_title, p_desc) in enumerate(pillars):
        px = MARGIN_X + (i * (pillar_w + Inches(0.3)))
        add_card(slide, px, pillar_y, pillar_w, pillar_h, fill_color=COLOR_WHITE, border_color=None)

        tb_pl = slide.shapes.add_textbox(px + Inches(0.4), pillar_y + Inches(0.4), pillar_w - Inches(0.8), pillar_h - Inches(0.8))
        tf_pl = tb_pl.text_frame
        tf_pl.word_wrap = True
        tf_pl.margin_left = tf_pl.margin_right = tf_pl.margin_top = tf_pl.margin_bottom = 0

        p_pt = tf_pl.paragraphs[0]
        p_pt.text = f"⚡  {p_title}"
        p_pt.font.name = FONT_PRIMARY
        p_pt.font.size = Pt(18)
        p_pt.font.bold = True
        p_pt.font.color.rgb = COLOR_DARK_TEXT

        p_pd = tf_pl.add_paragraph()
        p_pd.text = f"\n{p_desc}"
        p_pd.font.name = FONT_PRIMARY
        p_pd.font.size = Pt(14)
        p_pd.font.color.rgb = COLOR_DARK_TEXT

    add_footer(slide, brand)


def build_slide_14_source_base(slide, data: Dict[str, Any]):
    """Slide 14: The Source Base: Citations Matrix Table & Lever Badges."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="THE SOURCE BASE",
        title="Where these answers come from",
        subtitle=None,
    )

    table_y = Inches(2.4)
    table_w = CONTENT_WIDTH
    table_h = Inches(5.0)

    # Outer table container
    add_card(slide, MARGIN_X, table_y, table_w, table_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CARD_BORDER)

    # Table Header Row
    header_box = slide.shapes.add_textbox(MARGIN_X + Inches(0.4), table_y + Inches(0.2), table_w - Inches(0.8), Inches(0.5))
    tf_h = header_box.text_frame
    tf_h.margin_left = tf_h.margin_right = tf_h.margin_top = tf_h.margin_bottom = 0
    p_th = tf_h.paragraphs[0]
    p_th.text = f"{'SOURCE TYPE':<25} {'IN THE DATA':<25} {'WHY IT MATTERS':<35} {'LEVER':>10}"
    p_th.font.name = FONT_PRIMARY
    p_th.font.size = Pt(14)
    p_th.font.bold = True
    p_th.font.color.rgb = COLOR_MUTED_SLATE

    sources = [
        ("Editorial & review media", "~38% of AI responses", "Competitors dominate; client rarely mentioned", "Content"),
        ("Video & YouTube channels", "31.5% of AI responses", "High search reach; comparison reviews cited", "Monitor"),
        ("Brand-owned official sites", "Only 4.1% of AI responses", "Competitors cited 3x more than client domain", "Content"),
        ("Forums & Reddit communities", "18.2% of AI responses", "Unfiltered user discussions shape LLM sentiment", "Engage"),
    ]

    for i, (stype, in_data, why, lever) in enumerate(sources):
        row_y = table_y + Inches(0.9) + (i * Inches(0.9))

        tb_row = slide.shapes.add_textbox(MARGIN_X + Inches(0.4), row_y, table_w - Inches(0.8), Inches(0.8))
        tf_r = tb_row.text_frame
        tf_r.word_wrap = True
        tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0

        p = tf_r.paragraphs[0]
        p.text = f"• {stype:<25} {in_data:<24} {why:<35} [{lever}]"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(15)
        p.font.bold = (lever == "Content")
        p.font.color.rgb = COLOR_WHITE

    # Bottom Takeaway Banner
    add_takeaway_banner(
        slide=slide,
        points=[
            "Focus on the sources AI trusts most.",
            "Prioritize editorial publisher content and community discussions.",
            "Monitor YouTube and brand-owned channels over time.",
        ],
        y=Inches(7.8),
        h=Inches(1.6),
    )

    add_footer(slide, brand)


def build_slide_15_always_on(slide, data: Dict[str, Any]):
    """Slide 15: Underneath Both Workstreams: Always-On Category Intelligence."""
    set_slide_background(slide, COLOR_OBSIDIAN)
    brand = data.get("brand", "Your Brand")

    add_header(
        slide=slide,
        kicker="UNDERNEATH BOTH WORKSTREAMS",
        title="Always-on category intelligence",
        subtitle=None,
    )

    card_w = (CONTENT_WIDTH - Inches(0.6)) / 3
    card_h = Inches(5.0)
    card_y = Inches(2.8)

    cards = [
        ("📡  Daily Tracking", "Continuous monitoring of brand coverage, position, and sentiment across ChatGPT, Gemini, and Perplexity."),
        ("🎯  Prompt Fan-Outs", "Live tracking of related user query clusters, consumer follow-up questions, and emergent competitor citations."),
        ("🛡  Risk & Defense", "Instant detection of negative hallucinations, bot crawler errors, and algorithmic competitor displacement."),
    ]

    for i, (c_title, c_desc) in enumerate(cards):
        cx = MARGIN_X + (i * (card_w + Inches(0.3)))
        add_card(slide, cx, card_y, card_w, card_h, fill_color=COLOR_CARD_SLATE, border_color=COLOR_CYAN)

        tb = slide.shapes.add_textbox(cx + Inches(0.6), card_y + Inches(0.8), card_w - Inches(1.2), card_h - Inches(1.6))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p_t = tf.paragraphs[0]
        p_t.text = c_title
        p_t.font.name = FONT_PRIMARY
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE

        p_d = tf.add_paragraph()
        p_d.text = f"\n{c_desc}"
        p_d.font.name = FONT_PRIMARY
        p_d.font.size = Pt(16)
        p_d.font.color.rgb = COLOR_MUTED_SLATE

    # Bottom Callout Card
    add_takeaway_banner(
        slide=slide,
        points=["Continuous measurement turns GEO from a one-time project into an enduring competitive moat."],
        y=Inches(8.2),
        h=Inches(1.4),
        header_text="THE OPERATIONAL ADVANTAGE:",
    )

    add_footer(slide, brand)
