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

    def test_get_brand_stats_includes_required_query_params(self):
        with patch.object(self.client, "_get", return_value={"summary": {}}) as mock_get:
            self.client.get_brand_stats(
                "rep_123", country="id", start_date="2026-08-01", end_date="2026-08-31"
            )
            mock_get.assert_called_once_with(
                "/reports/brand/rep_123/stats",
                params={
                    "country": "id",
                    "startDate": "2026-08-01",
                    "endDate": "2026-08-31",
                },
            )

    def test_get_citations_includes_required_query_params(self):
        with patch.object(self.client, "_get", return_value={"items": []}) as mock_get:
            self.client.get_citations(
                "rep_123", country="id", start_date="2026-08-01", end_date="2026-08-31", limit=15
            )
            mock_get.assert_called_once_with(
                "/reports/brand/rep_123/citations",
                params={
                    "country": "id",
                    "startDate": "2026-08-01",
                    "endDate": "2026-08-31",
                    "limit": 15,
                },
            )

    def test_get_recommendations_includes_country_param(self):
        with patch.object(self.client, "_get", return_value=[]) as mock_get:
            self.client.get_recommendations("rep_123", country="id", limit=5)
            mock_get.assert_called_once_with(
                "/reports/brand/rep_123/recommendations",
                params={"country": "id"},
            )

    def test_fetch_pitch_intel_handles_real_openapi_dict_structure(self):
        report = {
            "id": "01M0DRRF1FNYGNW20W0Q916HB1",
            "brand": "Auto2000",
            "brandDomain": "auto2000.co.id",
            "countries": ["id"],
        }
        stats = {
            "id": "01M0DRRF1FNYGNW20W0Q916HB1",
            "summary": {
                "shareOfVoice": 0.18,
                "averageRank": 2.1,
                "totalMentions": 42,
            },
            # Real OpenAPI schema: competitorBrandsAnalysis is an object containing brandMentions array
            "competitorBrandsAnalysis": {
                "brandMentions": [
                    {"brand": "Toyota Astra", "shareOfVoice": 0.52, "averageRank": 1.1, "isMainBrand": False},
                    {"brand": "Daihatsu", "shareOfVoice": 0.30, "averageRank": 2.5, "isMainBrand": False},
                ],
                "brandCoverageHistory": [],
                "domainCoverageHistory": [],
            },
        }
        crawler = {
            "totalAgentVisits": 120,
            "pagesVisited": 15,
            "topEngine": "chatgpt",
        }
        # Real OpenAPI schema: citations use url and citations
        citations = [
            {"domain": "kompas.com", "citations": 88, "url": "https://kompas.com/oto/1", "title": "Top Dealer"},
        ]
        # Real OpenAPI schema: recommendations
        recommendations = [
            {
                "id": "rec_auto_1",
                "priority": 5,
                "type": "content_partnership_opportunities",
                "copy": {
                    "title": "Partner with Otomotif Media",
                    "reasoning": "High AI citation volume.",
                },
            }
        ]

        with patch.object(self.client, "find_brand_report", return_value=report):
            with patch.object(self.client, "get_brand_stats", return_value=stats):
                with patch.object(self.client, "get_agent_analytics", return_value=crawler):
                    with patch.object(self.client, "get_citations", return_value=citations):
                        with patch.object(self.client, "get_recommendations", return_value=recommendations):
                            intel = self.client.fetch_pitch_intel("Auto2000", "auto2000.co.id")
                            self.assertIsNotNone(intel)
                            self.assertEqual(intel["hero_stat"]["share_of_voice_pct"], 18.0)
                            self.assertEqual(len(intel["competitor_gap"]), 2)
                            self.assertEqual(intel["competitor_gap"][0]["competitor"], "Toyota Astra")
                            self.assertEqual(intel["competitor_gap"][0]["share_of_voice_pct"], 52.0)
                            self.assertEqual(intel["citation_matrix"][0]["volume"], 88)
                            self.assertEqual(intel["citation_matrix"][0]["citation_url"], "https://kompas.com/oto/1")
                            self.assertEqual(intel["retainer_actions"][0]["title"], "Partner with Otomotif Media")

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
