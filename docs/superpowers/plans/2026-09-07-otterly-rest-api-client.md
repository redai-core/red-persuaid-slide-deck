# Otterly.ai Public REST API Client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a native, zero-dependency Otterly.ai Public REST API client in Python (`engine/otterly_client.py`), extend credential management for `OTTERLY_API_KEY`, seamlessly integrate auto-detection into `scripts/run_audit_pipeline.py`, update `SKILL.md` to v1.6.0, and enforce a strict zero-write policy to eliminate external MCP overhead while preserving all slide deck archetypes.

**Architecture:** A standalone, read-only Python HTTP client built using standard library `urllib` communicates with `https://data.otterly.ai/v1`. It resolves credentials via `engine/credentials.py` (CLI flag -> `OTTERLY_API_KEY` env var -> `~/.persuaid/credentials.json`). `scripts/run_audit_pipeline.py` auto-detects credentials to fetch pre-configured Otterly brand intel and embed it into `metrics.json` and `otterly_intel.json`, falling back cleanly to the Apify search runner if no report exists.

**Tech Stack:** Python 3.10+ (Standard Library: `urllib.request`, `json`, `ssl`, `argparse`, `unittest`), Bash, Git.

---

## File Structure

- **Create**:
  - `engine/otterly_client.py`: Core zero-dependency read-only client and CLI runner.
  - `tests/test_credentials.py`: Unit tests for Otterly credential resolution and storage.
  - `tests/test_otterly_client.py`: Unit tests for `OtterlyClient` request formatting, zero-write enforcement, error handling, and payload normalization.
- **Modify**:
  - `engine/credentials.py`: Add `resolve_otterly_key`, `has_otterly_key`, and update `store_token`.
  - `scripts/run_audit_pipeline.py`: Add auto-detection of Otterly key, `--otterly-key` and `--no-otterly` CLI arguments, and fallback handling.
  - `SKILL.md`: Update version to `1.6.0`, update Step 1.5 instructions from MCP to REST API client CLI.

---

## Tasks

### Task 1: Extend Credential Manager for Otterly API Key

**Files:**
- Modify: `engine/credentials.py`
- Test: `tests/test_credentials.py`

- [ ] **Step 1: Write the failing unit tests for Otterly credential resolution**

Create `tests/test_credentials.py`:
```python
import os
import unittest
from unittest.mock import patch
from engine.credentials import (
    resolve_otterly_key,
    has_otterly_key,
    store_token,
    get_stored_token,
)

class TestOtterlyCredentials(unittest.TestCase):
    def test_resolve_otterly_key_override(self):
        with patch("engine.credentials.store_token") as mock_store:
            key = resolve_otterly_key(override="test_key_123")
            self.assertEqual(key, "test_key_123")
            mock_store.assert_called_once_with("test_key_123", key="otterly_api_key")

    def test_resolve_otterly_key_env_var(self):
        with patch.dict(os.environ, {"OTTERLY_API_KEY": "env_key_456"}, clear=False):
            key = resolve_otterly_key(override=None)
            self.assertEqual(key, "env_key_456")

    def test_resolve_otterly_key_stored_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("engine.credentials.get_stored_token", return_value="stored_key_789") as mock_get:
                key = resolve_otterly_key(override=None)
                self.assertEqual(key, "stored_key_789")
                mock_get.assert_called_once_with("otterly_api_key")

    def test_has_otterly_key_false_when_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("engine.credentials.get_stored_token", return_value=None):
                self.assertFalse(has_otterly_key())

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_credentials.py`
Expected: FAIL with `ImportError: cannot import name 'resolve_otterly_key' from 'engine.credentials'`

- [ ] **Step 3: Implement `resolve_otterly_key` and `has_otterly_key` in `engine/credentials.py`**

Modify `engine/credentials.py` to add:
```python
def resolve_otterly_key(override: Optional[str] = None) -> Optional[str]:
    """
    Resolves the active Otterly API key in priority order:
    1. Direct override (e.g. from CLI --otterly-key) -> automatically persists locally
    2. OTTERLY_API_KEY environment variable
    3. Stored token in ~/.persuaid/credentials.json under "otterly_api_key"
    Returns None if no key is configured.
    """
    if override and override.strip():
        token = override.strip()
        try:
            store_token(token, key="otterly_api_key")
        except Exception:
            pass
        return token

    env_token = os.environ.get("OTTERLY_API_KEY")
    if env_token and env_token.strip():
        return env_token.strip()

    return get_stored_token("otterly_api_key")


def has_otterly_key() -> bool:
    """Returns True if an Otterly API key is available in environment or local config."""
    return resolve_otterly_key() is not None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_credentials.py`
Expected: `Ran 4 tests in ... OK`

- [ ] **Step 5: Commit**

```bash
git add engine/credentials.py tests/test_credentials.py
git commit -m "feat(credentials): add Otterly API key resolution and storage"
```

---

### Task 2: Build Zero-Dependency Read-Only `OtterlyClient`

**Files:**
- Create: `engine/otterly_client.py`
- Test: `tests/test_otterly_client.py`

- [ ] **Step 1: Write the failing tests for `OtterlyClient`**

Create `tests/test_otterly_client.py`:
```python
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
                {"id": "rep_456", "brand": "Electrum", "brandDomain": "electrum.id"}
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
                "totalMentions": 15
            },
            "competitorBrandsAnalysis": [
                {"brand": "Alva", "shareOfVoice": 0.45, "averageRank": 1.2}
            ]
        }
        crawler = {
            "totalAgentVisits": 340,
            "pagesVisited": 28,
            "topEngine": "ChatGPT",
            "trend": [{"date": "2026-09-01", "visits": 42}]
        }
        citations = {
            "items": [
                {"domain": "kompas.com", "volume": 12, "citationUrl": "https://kompas.com/article1"},
                {"domain": "detik.com", "volume": 8, "citationUrl": "https://detik.com/article2"}
            ]
        }
        recommendations = {
            "items": [
                {
                    "id": "rec_1",
                    "priority": "HIGH",
                    "copy": {"title": "Enable Server-Side Rendering for LLMs", "reasoning": "Bot JS hydration failing."}
                }
            ]
        }

        with patch.object(self.client, "find_brand_report", return_value=report):
            with patch.object(self.client, "get_brand_stats", return_value=stats):
                with patch.object(self.client, "get_agent_analytics", return_value=crawler):
                    with patch.object(self.client, "get_citations", return_value=citations.get("items")):
                        with patch.object(self.client, "get_recommendations", return_value=recommendations.get("items")):
                            intel = self.client.fetch_pitch_intel("Electrum", "electrum.id")
                            self.assertIsNotNone(intel)
                            self.assertIn("hero_stat", intel)
                            self.assertIn("smoking_gun", intel)
                            self.assertIn("competitor_gap", intel)
                            self.assertIn("citation_matrix", intel)
                            self.assertIn("retainer_actions", intel)
                            self.assertEqual(intel["hero_stat"]["share_of_voice_pct"], 12.0)
                            self.assertEqual(intel["smoking_gun"]["total_agent_visits"], 340)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_otterly_client.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.otterly_client'`

- [ ] **Step 3: Implement `engine/otterly_client.py` with zero dependencies and CLI**

Create `engine/otterly_client.py`:
```python
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

    def get_brand_stats(self, report_id: str) -> Dict[str, Any]:
        """Fetches aggregate brand report statistics and competitor comparisons."""
        return self._get(f"/reports/brand/{report_id}/stats")

    def get_agent_analytics(self, report_id: str) -> Dict[str, Any]:
        """Fetches AI crawler server log statistics (GPTBot, ClaudeBot, etc.)."""
        try:
            return self._get(f"/reports/brand/{report_id}/agent-analytics/stats")
        except Exception:
            return {}

    def get_citations(self, report_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetches top cited authority sources and domains."""
        try:
            res = self._get(f"/reports/brand/{report_id}/citations", params={"limit": limit})
            return res.get("items", []) if isinstance(res, dict) else []
        except Exception:
            return []

    def get_recommendations(self, report_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetches actionable technical suggestions and prompt improvements."""
        try:
            res = self._get(f"/reports/brand/{report_id}/recommendations", params={"limit": limit})
            return res.get("items", []) if isinstance(res, dict) else []
        except Exception:
            return []

    def fetch_pitch_intel(self, brand_name: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        High-level aggregator: searches for a pre-configured report, pulls all read-only analytics,
        and packages them directly into the 4 Pitch Proof Weapons schema.
        Returns None if no matching pre-configured report is found.
        """
        report = self.find_brand_report(brand_name, domain)
        if not report:
            return None

        report_id = report.get("id")
        stats = self.get_brand_stats(report_id)
        crawler = self.get_agent_analytics(report_id)
        citations = self.get_citations(report_id, limit=20)
        recommendations = self.get_recommendations(report_id, limit=10)

        summary = stats.get("summary", {})
        comp_analysis = stats.get("competitorBrandsAnalysis", [])

        # 1. ARCH-HERO-STAT: The Wake-Up Call
        hero_stat = {
            "brand": report.get("brand"),
            "share_of_voice_pct": round(summary.get("shareOfVoice", 0) * 100, 1),
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests/test_otterly_client.py`
Expected: `Ran 5 tests in ... OK`

- [ ] **Step 5: Commit**

```bash
git add engine/otterly_client.py tests/test_otterly_client.py
git commit -m "feat(engine): add zero-dependency read-only OtterlyClient and CLI"
```

---

### Task 3: Integrate Otterly Intel Auto-Detection into `scripts/run_audit_pipeline.py`

**Files:**
- Modify: `scripts/run_audit_pipeline.py`

- [ ] **Step 1: Check existing imports and signature of `run_pipeline` in `scripts/run_audit_pipeline.py`**

Confirm line locations around argument parsing and execution flow.

- [ ] **Step 2: Add Otterly arguments and credential resolution**

In `scripts/run_audit_pipeline.py`:
- Import `resolve_otterly_key`, `has_otterly_key` from `engine.credentials`.
- Import `OtterlyClient` from `engine.otterly_client`.
- Add parameters to `run_pipeline`: `otterly_key: Optional[str] = None`, `no_otterly: bool = False`.
- In `run_pipeline`, prior to or alongside the journey generation:
  ```python
  otterly_intel = None
  if not no_otterly and (has_otterly_key() or otterly_key):
      try:
          otterly_client = OtterlyClient(api_key=otterly_key)
          print(f"[*] Checking Otterly API for pre-configured report for '{brand}'...")
          otterly_intel = otterly_client.fetch_pitch_intel(brand, domain)
          if otterly_intel:
              print(f"[✓] Ingested Otterly pitch intelligence for '{brand}' (SoV: {otterly_intel['hero_stat']['share_of_voice_pct']}%)")
              intel_path = Path(out_dir) / "otterly_intel.json"
              intel_path.write_text(json.dumps(otterly_intel, indent=2), encoding="utf-8")
          else:
              print(f"[Otterly API: No pre-configured report found for '{brand}'. Preserving credits and proceeding with standard live Apify audit.]")
      except Exception as e:
          print(f"[Otterly API Notice: {e}. Proceeding with standard live Apify audit.]")
  ```
- When writing `metrics.json`:
  ```python
  if otterly_intel:
      summary["otterly_intel"] = otterly_intel
  ```
- In `main()` CLI argument parsing:
  - Add `--otterly-key` (default `None`)
  - Add `--no-otterly` (action `store_true`, default `False`)

- [ ] **Step 3: Test CLI help and execution fallback without errors**

Run: `python3 scripts/run_audit_pipeline.py --help`
Verify that `--otterly-key` and `--no-otterly` appear in options.

- [ ] **Step 4: Commit**

```bash
git add scripts/run_audit_pipeline.py
git commit -m "feat(pipeline): integrate Otterly pitch intelligence auto-detection and fallback"
```

---

### Task 4: Upgrade `SKILL.md` to v1.6.0 and Repackage Bundle

**Files:**
- Modify: `SKILL.md`
- Run: `./package.sh`

- [ ] **Step 1: Update version header in `SKILL.md`**

Bump version announcement to:
`[PersuAId v1.6.0 - Otterly REST API Intelligence Active]`

- [ ] **Step 2: Update Step 1.5 Otterly section in `SKILL.md`**

Replace MCP tool references with direct REST API / CLI usage:
```markdown
#### A. Otterly REST API Pitch Intelligence Check (Strict Read-Only)
If an Otterly API key is configured (`OTTERLY_API_KEY` in environment or `~/.persuaid/credentials.json`):
1. **Zero-Write Safety Protocol**:
   - PersuAId uses native read-only REST calls (`engine/otterly_client.py`).
   - Mutation and creation endpoints are never called, ensuring zero accidental credit consumption.
2. **Pre-configured Report Lookup**:
   - Run: `python3 -m engine.otterly_client --brand "<Brand>" --domain "<domain>"`
   - Or allow `scripts/run_audit_pipeline.py` to auto-detect and ingest it into `metrics.json`.
   - **Match Found**: Ingests the 5 Pitch Proof Weapons (`hero_stat`, `smoking_gun`, `competitor_gap`, `citation_matrix`, `retainer_actions`) directly into slide archetypes.
   - **No Match Found**: Outputs:
     `[Otterly API: No pre-configured report found for '{brand}'. Preserving credits and proceeding with standard live Apify audit.]`
     Immediately continues to standard dual-platform Apify search journey modeling.
```

- [ ] **Step 3: Run `./package.sh` to compile bundle and synchronize to `~/.agents/skills/persuaid/`**

Run: `./package.sh`
Expected:
`✓ Successfully created: dist/persuaid.skill`
`✓ Local skill updated!`

- [ ] **Step 4: Run all unit tests to confirm zero regressions**

Run: `python3 -m unittest discover -s tests -p "test_*.py"`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "feat(skill): upgrade to v1.6.0 with Otterly REST API client workflow"
```

---

### Task 5: End-to-End Verification & Memory Synchronization

**Files:**
- Modify: Persistent memory (`reference-otterly-ai-mcp.md` or new `reference-otterly-api.md`)
- Modify: `MEMORY.md`

- [ ] **Step 1: Verify standalone CLI behavior**

Test with dummy key and missing brand to verify graceful exit:
Run: `python3 -m engine.otterly_client --brand "NonExistentBrand12345" --otterly-key "dummy_key"`
Expected: `[Otterly API: ...]` notice and exit code 2 or error output without unhandled Python stack trace.

- [ ] **Step 2: Update persistent memory files**

Update `/Users/dandydivaldy/.zcode/cli/memories/projects/red-persuaid-slide-deck-4b17e520a58f1589/memory/reference-otterly-ai-mcp.md` to document the transition to the direct REST API client (`engine/otterly_client.py`) and zero-write safety architecture.

- [ ] **Step 3: Final Git Status Check**

Run: `git status`
Verify everything is clean and properly tracked.
