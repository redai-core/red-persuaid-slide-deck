import json
import unittest
from unittest.mock import patch, MagicMock
from engine.otterly_client import OtterlyClient


class TestOtterlyClient(unittest.TestCase):
    def setUp(self):
        self.client = OtterlyClient(api_key="test_api_key")

    def test_init_raises_without_key(self):
        with patch("engine.otterly_client.resolve_otterly_key", return_value=None):
            with self.assertRaises(ValueError):
                OtterlyClient(api_key=None)

    def test_request_headers_include_bearer_token(self):
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({"status": "ok"}).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            data = self.client._get("/v1/engines")
            self.assertEqual(data, {"status": "ok"})

            req = mock_urlopen.call_args[0][0]
            self.assertEqual(req.get_header("Authorization"), "Bearer test_api_key")
            self.assertEqual(req.get_method(), "GET")

    def test_find_brand_report_matches_case_insensitive(self):
        mock_reports = {
            "items": [
                {"id": "rep_123", "brand": "Siloam Hospitals", "brandDomain": "siloamhospitals.com"},
                {"id": "rep_456", "brand": "Electrum", "brandDomain": "electrum.id"},
            ]
        }
        with patch.object(self.client, "_get", return_value=mock_reports):
            report = self.client.find_brand_report("siloam hospitals")
            self.assertIsNotNone(report)
            self.assertEqual(report["id"], "rep_123")

    def test_find_brand_report_returns_none_when_missing(self):
        mock_reports = {"items": []}
        with patch.object(self.client, "_get", return_value=mock_reports):
            report = self.client.find_brand_report("NonExistentBrand")
            self.assertIsNone(report)

    def test_fetch_pitch_intel_normalizes_weapons(self):
        report = {"id": "rep_123", "brand": "Electrum", "brandDomain": "electrum.id"}
        stats = {
            "summary": {
                "shareOfVoice": 0.12,
                "averageRank": 3.4,
                "totalMentions": 15,
            },
            "competitorBrandsAnalysis": [
                {"brand": "Alva", "shareOfVoice": 0.45, "averageRank": 1.2}
            ],
        }
        crawler = {
            "totalAgentVisits": 340,
            "pagesVisited": 28,
            "topEngine": "ChatGPT",
            "trend": [{"date": "2026-09-01", "visits": 42}],
        }
        citations = [
            {"domain": "kompas.com", "volume": 12, "citationUrl": "https://kompas.com/article1"},
            {"domain": "detik.com", "volume": 8, "citationUrl": "https://detik.com/article2"},
        ]
        recommendations = [
            {
                "id": "rec_1",
                "priority": "HIGH",
                "copy": {
                    "title": "Enable Server-Side Rendering for LLMs",
                    "reasoning": "Bot JS hydration failing.",
                },
            }
        ]

        with patch.object(self.client, "find_brand_report", return_value=report):
            with patch.object(self.client, "get_brand_stats", return_value=stats):
                with patch.object(self.client, "get_agent_analytics", return_value=crawler):
                    with patch.object(self.client, "get_citations", return_value=citations):
                        with patch.object(self.client, "get_recommendations", return_value=recommendations):
                            intel = self.client.fetch_pitch_intel("Electrum", "electrum.id")
                            self.assertIsNotNone(intel)
                            self.assertIn("hero_stat", intel)
                            self.assertIn("smoking_gun", intel)
                            self.assertIn("competitor_gap", intel)
                            self.assertIn("citation_matrix", intel)
                            self.assertIn("retainer_actions", intel)
                            self.assertEqual(intel["hero_stat"]["share_of_voice_pct"], 12.0)
                            self.assertEqual(intel["smoking_gun"]["total_agent_visits"], 340)
                            self.assertEqual(len(intel["competitor_gap"]), 1)
                            self.assertEqual(intel["competitor_gap"][0]["competitor"], "Alva")
                            self.assertEqual(intel["competitor_gap"][0]["gap_pct"], 33.0)


if __name__ == "__main__":
    unittest.main()
