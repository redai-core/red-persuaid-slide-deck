#!/usr/bin/env python3
"""
PersuAId DeckCraft Slide Composers
Exports builders for all 21 slides across Acts 1 to 4.
"""

from engine.deckcraft.slides.act1_education import (
    build_slide_01_cover,
    build_slide_02_legal,
    build_slide_03_shift,
    build_slide_04_comparison,
    build_slide_05_ecosystem,
)
from engine.deckcraft.slides.act2_diagnosis import (
    build_slide_06_divider_brand,
    build_slide_07_hero_diagnosis,
    build_slide_08_divider_intent,
    build_slide_09_competitor_gap,
    build_slide_10_engine_coverage,
    build_slide_11_verbatim_quotes,
)
from engine.deckcraft.slides.act3_threats import (
    build_slide_12_competitor_matrix,
    build_slide_13_owned_assets,
    build_slide_14_source_base,
    build_slide_15_always_on,
)
from engine.deckcraft.slides.act4_commercials import (
    build_slide_16_measurement,
    build_slide_17_divider_appendix,
    build_slide_18_case_studies,
    build_slide_19_geo_tools_demo,
    build_slide_20_retainer_sow,
    build_slide_21_closer,
)

ALL_SLIDE_BUILDERS = [
    build_slide_01_cover,
    build_slide_02_legal,
    build_slide_03_shift,
    build_slide_04_comparison,
    build_slide_05_ecosystem,
    build_slide_06_divider_brand,
    build_slide_07_hero_diagnosis,
    build_slide_08_divider_intent,
    build_slide_09_competitor_gap,
    build_slide_10_engine_coverage,
    build_slide_11_verbatim_quotes,
    build_slide_12_competitor_matrix,
    build_slide_13_owned_assets,
    build_slide_14_source_base,
    build_slide_15_always_on,
    build_slide_16_measurement,
    build_slide_17_divider_appendix,
    build_slide_18_case_studies,
    build_slide_19_geo_tools_demo,
    build_slide_20_retainer_sow,
    build_slide_21_closer,
]
