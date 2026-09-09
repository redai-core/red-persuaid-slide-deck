#!/usr/bin/env python3
"""
Unit tests for QuickSlide integration mechanics:
- Physical text budgets (estimate_char_budget, trim_to_char_budget)
- Copy guard sanitization (markdown stripping, anti-leak filters)
- Local copy repair (sentence completion, deduplication)
- DeckCraft metrics normalization without silent fallbacks
- Staging validation with automatic clean-up
"""

import unittest
from engine.text_budget import estimate_char_budget, trim_to_char_budget, drop_truncated_tail
from engine.copy_guard import sanitize_generated_copy, is_meta_copy
from engine.copy_repair import finish_claim, uniquify_texts
from engine.deckcraft.builder import DeckCraftBuilder
from engine.staging_manager import DeckStagingManager


class TestTextBudget(unittest.TestCase):
    def test_estimate_char_budget(self):
        # 4 inch wide, 2 inch high box at 16pt font
        width_emu = 4 * 914400
        height_emu = 2 * 914400
        budget = estimate_char_budget(width_emu=width_emu, height_emu=height_emu, font_size_pt=16, role="body")
        self.assertIsNotNone(budget)
        self.assertGreater(budget, 50)
        self.assertLessEqual(budget, 800)

    def test_trim_to_char_budget_no_word_cut(self):
        text = "Auto2000 commands a dominant market share across digital channels in Indonesia."
        trimmed = trim_to_char_budget(text, max_chars=40)
        self.assertLessEqual(len(trimmed), 40)
        self.assertFalse(trimmed.endswith("share acro"))
        self.assertTrue(trimmed.endswith("."))


class TestCopyGuardAndRepair(unittest.TestCase):
    def test_sanitize_markdown(self):
        raw = "Slide 1 — **Executive Summary:** Auto2000 captures [22% SoV](https://otterly.ai) overall."
        cleaned = sanitize_generated_copy(raw)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("[22% SoV]", cleaned)
        self.assertNotIn("Slide 1 —", cleaned)
        self.assertIn("22% SoV", cleaned)

    def test_is_meta_copy(self):
        self.assertTrue(is_meta_copy("Write for this slot only"))
        self.assertTrue(is_meta_copy("do not copy template sample"))
        self.assertFalse(is_meta_copy("Auto2000 commands 22% Share of Voice in Jakarta."))

    def test_finish_claim(self):
        incomplete = "Auto2000 faces an acute citation gap with"
        finished = finish_claim(incomplete)
        self.assertFalse(finished.lower().endswith("with"))
        self.assertTrue(finished.endswith("."))

    def test_uniquify_texts(self):
        repeats = [
            "Auto2000 leads the automotive market with superior service quality.",
            "Auto2000 leads the automotive market with superior service quality.",
        ]
        varied = uniquify_texts(repeats)
        self.assertEqual(len(varied), 2)
        self.assertNotEqual(varied[0], varied[1])


class TestDeckCraftGroundedMetrics(unittest.TestCase):
    def test_raw_otterly_payload_no_silent_fallback(self):
        raw_payload = {
            "brand": "Auto2000",
            "category": "Automotive Dealership",
            "summary": {
                "shareOfVoice": 0.224,  # 22.4%
                "averageRank": 1.2,
            },
            "allBrandsAnalysis": {
                "brandMentions": [
                    {"brand": "Auto2000", "shareOfVoice": 0.224},
                    {"brand": "Mobil88", "shareOfVoice": 0.142},
                    {"brand": "Carsome", "shareOfVoice": 0.098},
                ]
            }
        }
        builder = DeckCraftBuilder(raw_payload)
        data = builder.data

        # Verify hero_stat reflects the real 22.4% and #1.2 rank, NOT the fake 9.3% or #4
        self.assertEqual(data["hero_stat"]["share_of_voice_pct"], 22.4)
        self.assertEqual(data["hero_stat"]["average_rank"], "#1.2")

        # Verify competitor gap extracted Mobil88 and Carsome with real numbers
        competitors = [c["competitor"] for c in data["competitor_gap"]]
        self.assertIn("Mobil88", competitors)
        self.assertIn("Carsome", competitors)
        mobil88_stat = next(c for c in data["competitor_gap"] if c["competitor"] == "Mobil88")
        self.assertEqual(mobil88_stat["share_of_voice_pct"], 14.2)


class TestStagingSanitization(unittest.TestCase):
    def test_stage_act_cleans_markdown_and_repairs(self):
        mgr = DeckStagingManager()
        session = mgr.create_session(brand="Auto2000", category="Automotive")
        sid = session["session_id"]

        act_slides = [
            {
                "slide_number": 1,
                "archetype_id": "ARCH-COVER",
                "slots": {
                    "kicker": "**EXECUTIVE BRIEF**",
                    "headline": "Slide 1 — Auto2000 GEO Strategy Deck",
                    "subtitle": "Comprehensive AI search audit across ChatGPT and Google.",
                }
            }
        ]
        result = mgr.stage_act(sid, "Act I", act_slides)
        self.assertTrue(result["validation_passed"])

        staged_slide = mgr.get_session(sid)["slides"]["1"]
        # Verify markdown stripped and prefix removed
        self.assertEqual(staged_slide["slots"]["kicker"], "EXECUTIVE BRIEF")
        self.assertEqual(staged_slide["slots"]["headline"], "Auto2000 GEO Strategy Deck.")


if __name__ == "__main__":
    unittest.main()
