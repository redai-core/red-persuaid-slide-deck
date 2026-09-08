#!/usr/bin/env python3
"""
Unit tests for PersuAId Universal Template Decompiler,
Staging Session Manager, and Act-by-Act Compiler.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from engine.template_profile import TemplateProfile, ArchetypeSpec, SlotContract, ElementGeometry
from engine.template_decompiler import TemplateDecompiler, decompile_pptx_file
from engine.staging_manager import DeckStagingManager
from engine.universal_compiler import UniversalDeckCompiler
from engine.mcp_server import (
    handle_persuaid_learn_template,
    handle_persuaid_init_session,
    handle_persuaid_get_archetypes,
    handle_persuaid_stage_act,
    handle_persuaid_compile_session,
)


class TestUniversalTemplate(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.ref_pptx = Path("/Users/dandydivaldy/Downloads/Electrum AI Visibility CONVR.pptx")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_template_profile_serialization(self):
        profile = TemplateProfile(
            template_id="test_tmpl",
            name="Test Template",
            archetypes={
                "ARCH-HERO-STAT": ArchetypeSpec(
                    archetype_id="ARCH-HERO-STAT",
                    name="Hero Stat Grid",
                    description="4-column metric grid",
                    slots=[
                        SlotContract(slot_id="kicker", role="kicker", max_chars=40),
                        SlotContract(slot_id="headline", role="action_headline", max_chars=120),
                    ],
                )
            },
        )
        json_str = profile.to_json()
        deserialized = TemplateProfile.from_json(json_str)
        self.assertEqual(deserialized.template_id, "test_tmpl")
        self.assertIn("ARCH-HERO-STAT", deserialized.archetypes)
        menu = deserialized.get_archetype_menu()
        self.assertEqual(len(menu), 1)
        self.assertEqual(menu[0]["archetype_id"], "ARCH-HERO-STAT")

    def test_decompile_pptx(self):
        if not self.ref_pptx.exists():
            self.skipTest("Reference PPTX not available on host")

        profile = decompile_pptx_file(str(self.ref_pptx))
        self.assertGreater(profile.canvas.width_inches, 0)
        self.assertGreater(profile.canvas.height_inches, 0)
        self.assertIsNotNone(profile.palette.background)
        self.assertIsNotNone(profile.palette.accent_primary)
        self.assertIn("ARCH-COVER", profile.archetypes)
        self.assertIn("ARCH-HERO-STAT", profile.archetypes)

    def test_staging_manager_session_lifecycle_and_validation(self):
        staging_dir = self.temp_path / "sessions"
        mgr = DeckStagingManager(sessions_dir=staging_dir)

        # 1. Initialize session
        init_res = mgr.create_session(
            brand="Auto2000",
            category="Toyota Dealer Network",
            competitors="Seva.id, CARRO",
            total_slides=5,
        )
        session_id = init_res["session_id"]
        self.assertTrue(session_id.startswith("sess_"))
        self.assertIn("archetype_menu", init_res)

        # 2. Query archetypes for Act I
        arch_res = mgr.get_archetypes_for_act(session_id, "Act I")
        self.assertEqual(arch_res["act"], "Act I")
        self.assertIn("ARCH-COVER", arch_res["archetypes"])

        # 3. Stage Act I with valid slide content
        valid_slides = [
            {
                "slide_number": 1,
                "archetype_id": "ARCH-COVER",
                "slots": {
                    "kicker": "EXECUTIVE STRATEGY BRIEFING",
                    "headline": "THE NEW BATTLE FOR AI VISIBILITY",
                    "subtitle": "Generative Engine Optimization Audit",
                },
            },
            {
                "slide_number": 2,
                "archetype_id": "ARCH-HERO-STAT",
                "slots": {
                    "kicker": "CORE FINDINGS",
                    "headline": "Auto2000 captures strong aftersales presence",
                    "card1_stat": "22%",
                    "card1_label": "Share of Voice",
                    "takeaway_banner": "Dominates branded queries but cedes discovery intent to aggregators.",
                },
            },
        ]
        stage_res = mgr.stage_act(session_id, "Act I", valid_slides)
        self.assertTrue(stage_res["validation_passed"])
        self.assertEqual(stage_res["staged_slides"], 2)
        self.assertEqual(len(stage_res["issues"]), 0)

        # 4. Test character budget overflow detection
        overflow_slides = [
            {
                "slide_number": 3,
                "archetype_id": "ARCH-HERO-STAT",
                "slots": {
                    "kicker": "THIS KICKER IS RIDICULOUSLY AND UNNECESSARILY LONG TO EXCEED THE CHARACTER LIMIT FOR TESTING PURPOSES TO ENSURE VALIDATOR CATCHES OVERFLOW",
                    "headline": "Testing overflow warning",
                },
            }
        ]
        overflow_res = mgr.stage_act(session_id, "Act II", overflow_slides)
        self.assertFalse(overflow_res["validation_passed"])
        self.assertGreater(len(overflow_res["issues"]), 0)
        self.assertEqual(overflow_res["issues"][0]["slot_id"], "kicker")

    def test_universal_compiler_end_to_end(self):
        staging_dir = self.temp_path / "sessions"
        mgr = DeckStagingManager(sessions_dir=staging_dir)

        init_res = mgr.create_session(
            brand="Auto2000",
            category="Toyota Dealer Network",
            total_slides=3,
        )
        session_id = init_res["session_id"]

        slides = [
            {
                "slide_number": 1,
                "archetype_id": "ARCH-COVER",
                "slots": {
                    "kicker": "EXECUTIVE BRIEF",
                    "headline": "AI SEARCH READINESS",
                    "subtitle": "6-Month Strategic Engagement",
                },
            },
            {
                "slide_number": 2,
                "archetype_id": "ARCH-HERO-STAT",
                "slots": {
                    "kicker": "CORE DIAGNOSIS",
                    "headline": "Auto2000 leads in service intent",
                    "card1_stat": "28%",
                    "card1_label": "Share of Voice",
                    "card2_stat": "#1",
                    "card2_label": "Authorized Network",
                    "takeaway_banner": "Aggregators dominate unbranded discovery; Auto2000 controls maintenance queries.",
                },
            },
            {
                "slide_number": 3,
                "archetype_id": "ARCH-CLOSER",
                "slots": {
                    "kicker": "ACTION MANDATE",
                    "closing_headline": "BE THE FIRST ANSWER IN 2026",
                    "closing_subtext": "Launch the 30-day quick wins sprint.",
                },
            },
        ]
        mgr.stage_act(session_id, "Full Deck", slides)

        compiler = UniversalDeckCompiler(staging_manager=mgr)
        compile_res = compiler.compile_session(session_id, out_dir=str(self.temp_path))

        self.assertEqual(compile_res["status"], "success")
        self.assertEqual(compile_res["total_slides"], 3)
        deck_path = Path(compile_res["deck_path"])
        self.assertTrue(deck_path.exists())
        self.assertGreater(deck_path.stat().st_size, 5000)

    def test_mcp_tool_handlers(self):
        # 1. persuaid_init_session
        init_res = handle_persuaid_init_session({
            "brand": "Siloam Hospitals",
            "category": "Healthcare Network",
            "total_slides": 4,
        })
        self.assertIn("session_id", init_res)
        session_id = init_res["session_id"]

        # 2. persuaid_get_archetypes
        arch_res = handle_persuaid_get_archetypes({
            "session_id": session_id,
            "act": "Act I",
        })
        self.assertIn("archetypes", arch_res)

        # 3. persuaid_stage_act
        stage_res = handle_persuaid_stage_act({
            "session_id": session_id,
            "act": "Act I",
            "slides": [
                {
                    "slide_number": 1,
                    "archetype_id": "ARCH-COVER",
                    "slots": {
                        "kicker": "HEALTHCARE GEO AUDIT",
                        "headline": "PATIENT DISCOVERY ON AI ENGINES",
                    },
                }
            ],
        })
        self.assertEqual(stage_res["staged_slides"], 1)

        # 4. persuaid_compile_session
        compile_res = handle_persuaid_compile_session({
            "session_id": session_id,
            "out_dir": str(self.temp_path),
        })
        self.assertEqual(compile_res["status"], "success")
        self.assertEqual(compile_res["total_slides"], 1)


if __name__ == "__main__":
    unittest.main()
