#!/usr/bin/env python3
"""
PersuAId Otterly.ai Public REST API Client
Retrieves ground-truth GEO brand analytics, citation market share, AI crawler logs,
and actionable technical recommendations via Otterly's public OpenAPI endpoints.

Strict Zero-Write Policy:
Only read operations (GET) are implemented. Mutation/creation endpoints (POST/PUT/DELETE)
are strictly omitted to prevent accidental credit burn or cost drain.
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.credentials import resolve_otterly_key


class OtterlyClient:
    BASE_URL = "https://data.otterly.ai/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = resolve_otterly_key(api_key)
        if not self.api_key:
            raise ValueError(
                "Otterly API key not found. Please provide your key via --otterly-key, "
                "the OTTERLY_API_KEY environment variable, or store it in ~/.persuaid/credentials.json."
            )
        self.ssl_context = ssl._create_unverified_context()

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Executes a GET request against the Otterly REST API."""
        url = f"{self.BASE_URL}{endpoint}" if endpoint.startswith("/") else f"{self.BASE_URL}/{endpoint}"
        if params:
            clean_params = {k: v for k, v in params.items() if v is not None}
            if clean_params:
                url = f"{url}?{urllib.parse.urlencode(clean_params)}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "PersuAId-Engine/1.6.0",
        }

        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                msg = err_json.get("message") or err_json.get("error", {}).get("message") or err_body
            except Exception:
                msg = err_body or str(e)
            raise RuntimeError(f"Otterly API HTTP {e.code} on {endpoint}: {msg}") from e
        except Exception as e:
            raise RuntimeError(f"Otterly API connection failure on {endpoint}: {str(e)}") from e

    def find_brand_report(self, brand_name: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Finds a pre-configured brand report matching brand_name or domain (case-insensitive)."""
        clean_brand = brand_name.strip().lower()
        clean_domain = domain.strip().lower() if domain else ""

        try:
            res = self._get("/reports/brand", params={"brand": brand_name})
            items = res.get("items", []) if isinstance(res, dict) else []
            for item in items:
                b = str(item.get("brand", "")).lower()
                d = str(item.get("brandDomain", "")).lower()
                if clean_brand == b or (clean_domain and clean_domain in d):
                    return item
            # If no direct match in filtered search, check all reports in workspace
            if not items:
                all_res = self._get("/reports/brand")
                all_items = all_res.get("items", []) if isinstance(all_res, dict) else []
                for item in all_items:
                    b = str(item.get("brand", "")).lower()
                    d = str(item.get("brandDomain", "")).lower()
                    if clean_brand in b or b in clean_brand or (clean_domain and clean_domain in d):
                        return item
        except Exception as e:
            print(f"Warning: Failed to search brand reports: {e}", file=sys.stderr)
            return None
        return None

    def get_brand_stats(
        self,
        report_id: str,
        country: str = "id",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        engines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Fetches aggregate brand report statistics and competitor comparisons."""
        now = datetime.now(timezone.utc).date()
        end_str = end_date or now.strftime("%Y-%m-%d")
        start_str = start_date or (now - timedelta(days=30)).strftime("%Y-%m-%d")
        params: Dict[str, Any] = {
            "country": country.lower(),
            "startDate": start_str,
            "endDate": end_str,
        }
        if engines:
            params["engines"] = engines
        return self._get(f"/reports/brand/{report_id}/stats", params=params)

    def get_agent_analytics(
        self,
        report_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetches AI crawler server log statistics (GPTBot, ClaudeBot, etc.)."""
        params: Dict[str, Any] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        try:
            return self._get(f"/reports/brand/{report_id}/agent-analytics/stats", params=params if params else None)
        except Exception:
            return {}

    def get_citations(
        self,
        report_id: str,
        country: str = "id",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Fetches top cited authority sources and domains."""
        now = datetime.now(timezone.utc).date()
        end_str = end_date or now.strftime("%Y-%m-%d")
        start_str = start_date or (now - timedelta(days=30)).strftime("%Y-%m-%d")
        params: Dict[str, Any] = {
            "country": country.lower(),
            "startDate": start_str,
            "endDate": end_str,
            "limit": limit,
        }
        try:
            res = self._get(f"/reports/brand/{report_id}/citations", params=params)
            return res.get("items", []) if isinstance(res, dict) else []
        except Exception:
            return []

    def get_recommendations(
        self,
        report_id: str,
        country: str = "id",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Fetches actionable technical suggestions and prompt improvements."""
        params: Dict[str, Any] = {
            "country": country.lower(),
        }
        try:
            res = self._get(f"/reports/brand/{report_id}/recommendations", params=params)
            if isinstance(res, list):
                return res[:limit]
            return res.get("items", [])[:limit] if isinstance(res, dict) else []
        except Exception:
            return []

    def fetch_pitch_intel(
        self,
        brand_name: str,
        domain: Optional[str] = None,
        country: Optional[str] = None,
        days: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """
        High-level aggregator: searches for a pre-configured report, pulls all read-only analytics,
        and packages them directly into the 4 Pitch Proof Weapons schema.
        Returns None if no matching pre-configured report is found.
        """
        report = self.find_brand_report(brand_name, domain)
        if not report:
            return None

        report_id = report.get("id")

        # Resolve country: explicit -> report.countries[0] -> default "id"
        target_country = country
        if not target_country:
            report_countries = report.get("countries", [])
            if report_countries and isinstance(report_countries, list) and len(report_countries) > 0:
                target_country = str(report_countries[0]).lower()
            else:
                target_country = "id"

        now = datetime.now(timezone.utc).date()
        end_date = now.strftime("%Y-%m-%d")
        start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")

        try:
            stats = self.get_brand_stats(
                report_id, country=target_country, start_date=start_date, end_date=end_date
            )
        except Exception as e:
            print(f"Warning: Failed to fetch brand stats for report {report_id}: {e}", file=sys.stderr)
            stats = {}

        crawler = self.get_agent_analytics(
            report_id, start_date=start_date, end_date=end_date
        )
        citations = self.get_citations(
            report_id, country=target_country, start_date=start_date, end_date=end_date, limit=20
        )
        recommendations = self.get_recommendations(
            report_id, country=target_country, limit=10
        )

        summary = stats.get("summary", {}) if isinstance(stats, dict) else {}
        comp_analysis = stats.get("competitorBrandsAnalysis", []) if isinstance(stats, dict) else []

        # 1. ARCH-HERO-STAT: The Wake-Up Call
        sov = summary.get("shareOfVoice")
        hero_stat = {
            "brand": report.get("brand"),
            "share_of_voice_pct": round(sov * 100, 1) if sov is not None else 0.0,
            "average_rank": summary.get("averageRank", 0),
            "total_mentions": summary.get("totalMentions", 0),
        }

        # 2. ARCH-TECH-AUDIT: The Smoking Gun (Bot Analytics)
        smoking_gun = {
            "total_agent_visits": crawler.get("totalAgentVisits", 0),
            "pages_visited": crawler.get("pagesVisited", 0),
            "top_engine": crawler.get("topEngine", "Unknown"),
            "trend": crawler.get("trend", []),
        }

        # 3. ARCH-GAP-BAR: Competitor Threat Matrix
        competitor_gap = []
        for comp in comp_analysis:
            competitor_gap.append({
                "competitor": comp.get("brand"),
                "share_of_voice_pct": round(comp.get("shareOfVoice", 0) * 100, 1),
                "average_rank": comp.get("averageRank", 0),
                "gap_pct": round((comp.get("shareOfVoice", 0) - summary.get("shareOfVoice", 0)) * 100, 1),
            })

        # 4. ARCH-SOURCE-MATRIX: Citation Hijack
        citation_matrix = []
        for c in citations[:10]:
            citation_matrix.append({
                "domain": c.get("domain"),
                "volume": c.get("volume", 0),
                "citation_url": c.get("citationUrl", ""),
            })

        # 5. ARCH-PRIORITY-ACTION: Retainer Scope of Work
        retainer_actions = []
        for rec in recommendations[:5]:
            copy = rec.get("copy", {})
            retainer_actions.append({
                "id": rec.get("id"),
                "priority": rec.get("priority", "MEDIUM"),
                "title": copy.get("title") or copy.get("headline") or "SEO Optimization",
                "reasoning": copy.get("reasoning") or copy.get("suggestions") or "",
            })

        return {
            "brand": report.get("brand"),
            "domain": report.get("brandDomain"),
            "report_id": report_id,
            "hero_stat": hero_stat,
            "smoking_gun": smoking_gun,
            "competitor_gap": competitor_gap,
            "citation_matrix": citation_matrix,
            "retainer_actions": retainer_actions,
        }


def main():
    parser = argparse.ArgumentParser(description="PersuAId Otterly.ai Public REST API Intel Fetcher")
    parser.add_argument("--brand", required=True, help="Brand name to query")
    parser.add_argument("--domain", default=None, help="Official domain (optional)")
    parser.add_argument("--otterly-key", default=None, help="Otterly API key override")
    parser.add_argument("--out-dir", default=".", help="Directory to save otterly_intel.json")
    args = parser.parse_args()

    try:
        client = OtterlyClient(api_key=args.otterly_key)
    except ValueError as e:
        print(f"[Otterly API: {e}]", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Querying Otterly REST API for pre-configured report: '{args.brand}'...")
    intel = client.fetch_pitch_intel(args.brand, args.domain)
    if not intel:
        print(
            f"[Otterly API: No pre-configured report found for '{args.brand}'. "
            "Preserving credits and falling back to standard live search.]"
        )
        sys.exit(2)

    out_path = Path(args.out_dir) / "otterly_intel.json"
    out_path.write_text(json.dumps(intel, indent=2), encoding="utf-8")
    print(f"[✓] Otterly pitch intelligence saved to: {out_path}")
    print(f"    - Brand: {intel['brand']} ({intel['domain']})")
    print(f"    - Share of Voice: {intel['hero_stat']['share_of_voice_pct']}% (Avg Rank: {intel['hero_stat']['average_rank']})")
    print(f"    - AI Crawler Visits: {intel['smoking_gun']['total_agent_visits']}")
    print(f"    - Top Cited Domains: {len(intel['citation_matrix'])}")
    print(f"    - Remediation Actions: {len(intel['retainer_actions'])}")


if __name__ == "__main__":
    main()
