# Design Spec: Otterly.ai Public REST API Client Integration

- **Date:** 2026-09-07
- **Status:** Approved
- **Target Version:** `PersuAId v1.6.0 - Otterly REST API Intelligence Active`

---

## 1. Context & Objectives

PersuAId pitch decks require high-conviction, ground-truth metrics (multi-engine visibility gaps, crawler server logs, competitor citation shares) to persuade C-suite executives and sell 30-day quick wins and 6-month retainers.

In PersuAId v1.5.0, Otterly.ai data was integrated via Model Context Protocol (`mcp__otterly__*`). While functional, configuring and authenticating an external Otterly MCP server (OAuth flow, streamable HTTP transport, local client configuration) introduces friction and setup hurdles.

### Core Goals:
1. **Direct REST API Client**: Replace the external MCP dependency with a native Python client (`engine/otterly_client.py`) using Otterly's public OpenAPI endpoints (`https://data.otterly.ai/v1`).
2. **Zero External Dependencies**: Use Python standard library (`urllib.request`, `json`, `ssl`), preserving the lightweight, dependency-free architecture of the `engine/` package.
3. **Strict Zero-Write Policy**: Ensure that the client only implements read queries (`GET`), strictly forbidding mutation/creation endpoints (`POST`, `PUT`, `DELETE`) to protect against credit burn or runaway costs.
4. **Seamless Auto-Detection**: Automatically detect `OTTERLY_API_KEY` (or `~/.persuaid/credentials.json`) in the audit pipeline, pulling pitch intelligence when available and falling back to the standard Apify runner when absent or if no report exists.
5. **Preserve All Existing Assets**: Keep the 16:9 HD widescreen canvas (`13.333" × 7.5"`), slide archetypes, visual hierarchy, and Apify live-search runners completely intact.

---

## 2. Architecture & Components

```
┌─────────────────────────────────────────────────────────────┐
│                       User / Agent                          │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼ (auto-detect)                ▼ (standalone CLI)
┌──────────────────────────────┐ ┌────────────────────────────┐
│ scripts/run_audit_pipeline.py│ │   engine/otterly_client.py  │
└──────────────┬───────────────┘ └────────────┬───────────────┘
               │                              │
               ▼                              ▼
��─────────────────────────────────────────────────────────────┐
│                    engine/otterly_client.py                 │
│              (Strict Read-Only REST API Client)             │
│        - GET /v1/reports/brand                              │
│        - GET /v1/reports/brand/{id}/stats                   │
│        - GET /v1/reports/brand/{id}/agent-analytics/stats   │
│        - GET /v1/reports/brand/{id}/citations               │
│        - GET /v1/reports/brand/{id}/recommendations         │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌───────────────────────────┐         ┌───────────────────────┐
│ Brand Report Matched      │         │ No Report / No Key    │
├───────────────────────────┤         ├───────────────────────┤
│ Ingest 4 Pitch Weapons    │         │ Clean fallback to     │
│ into metrics.json &       │         │ live Apify search     │
│ otterly_intel.json        │         │ runner (~18s)         │
└───────────────────────────┘         └───────────────────────┘
```

### Component 1: Credential Resolution (`engine/credentials.py`)
Add support for Otterly API credentials with the same security model as Apify:
- `resolve_otterly_key(override: Optional[str] = None) -> Optional[str]`:
  1. CLI override (`--otterly-key`) -> automatically persisted to `~/.persuaid/credentials.json`.
  2. `OTTERLY_API_KEY` environment variable.
  3. Stored key in `~/.persuaid/credentials.json` under `"otterly_api_key"`.
- `has_otterly_key() -> bool`: Returns `True` if any key source is available.
- `store_token(token, key="otterly_api_key")`: Saves token with strict `0600` (read/write owner-only) permissions.

### Component 2: Dedicated REST Client (`engine/otterly_client.py`)
- **Base URL**: `https://data.otterly.ai/v1`
- **Authentication**: `Authorization: Bearer <API_KEY>`
- **Methods**:
  - `find_brand_report(brand_name: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]`: Queries `GET /v1/reports/brand` and matches by brand name (case-insensitive) or domain.
  - `get_brand_stats(report_id: str) -> Dict[str, Any]`: Queries `GET /v1/reports/brand/{report_id}/stats`.
  - `get_agent_analytics(report_id: str) -> Dict[str, Any]`: Queries `GET /v1/reports/brand/{report_id}/agent-analytics/stats`.
  - `get_citations(report_id: str, limit: int = 20) -> List[Dict[str, Any]]`: Queries `GET /v1/reports/brand/{report_id}/citations`.
  - `get_recommendations(report_id: str, limit: int = 10) -> List[Dict[str, Any]]`: Queries `GET /v1/reports/brand/{report_id}/recommendations`.
  - `fetch_pitch_intel(brand_name: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]`: High-level aggregator returning the normalized 4 Pitch Proof Weapons dictionary.
- **Standalone CLI**:
  ```bash
  python3 -m engine.otterly_client --brand "Brand" [--domain "domain.com"] [--out-dir "."] [--otterly-key "key"]
  ```

### Component 3: Pipeline Integration (`scripts/run_audit_pipeline.py`)
- Automatically check `has_otterly_key()`.
- If `True` and not disabled via `--no-otterly`:
  - Call `OtterlyClient.fetch_pitch_intel(brand, domain)`.
  - If report found: embed payload under `"otterly_intel"` inside `metrics.json` and save `otterly_intel.json`.
  - If not found or API call fails: output clear informational message and proceed with standard Apify dual-platform search runner.

### Component 4: Skill Definition (`SKILL.md`)
- Bump version to `PersuAId v1.6.0 - Otterly REST API Intelligence Active`.
- Replace `mcp__otterly__*` tool references in Step 1.5 with direct pipeline/CLI execution instructions.
- Retain the exact archetype mappings for pitch generation.

---

## 3. Data Mapping: 4 Pitch Proof Weapons

The returned `otterly_intel` object normalizes API responses directly into PersuAId slide archetypes:

| Pitch Proof Weapon | Source API Endpoint | Output JSON Field | Target Slide Archetype | Key Metric Displayed |
|---|---|---|---|---|
| **1. The Wake-Up Call** | `/v1/reports/brand/{id}/stats` | `hero_stat` | `ARCH-HERO-STAT` | Multi-engine blind spots (e.g. ChatGPT visibility vs Perplexity vs Gemini) |
| **2. The Smoking Gun** | `/v1/reports/brand/{id}/agent-analytics/stats` | `smoking_gun` | `ARCH-TECH-AUDIT` | AI crawler server log activity (GPTBot, ClaudeBot visits, crawler trend) |
| **3. The Competitive Threat** | `/v1/reports/brand/{id}/stats` (`competitorBrandsAnalysis`) | `competitor_gap` | `ARCH-GAP-BAR` | Share of Voice % deltas and rank displacement against competitors |
| **4. Citation Hijack** | `/v1/reports/brand/{id}/citations` | `citation_matrix` | `ARCH-SOURCE-MATRIX` | Top cited authority root domains out-ranking official domain |
| **5. Retainer SOW** | `/v1/reports/brand/{id}/recommendations` | `retainer_actions` | `ARCH-PRIORITY-ACTION` | 30-day technical remediation tickets derived from audit recommendations |

---

## 4. Safety & Error Handling

1. **Zero-Write Enforcement**: The `OtterlyClient` class contains zero `POST`, `PUT`, or `DELETE` requests. Accidental report generation or quota-consuming mutations cannot occur.
2. **Graceful Fallback**: If the API key is missing, network fails, or no report matches the target brand, the system prints:
   `[Otterly API: No pre-configured report found for '{brand}'. Preserving credits and proceeding with standard live Apify audit.]`
   The audit pipeline continues uninterrupted with the Apify live runner.
3. **Timeout & SSL Handling**: Uses standard 30s timeouts and secure TLS contexts, handling `urllib.error.HTTPError` with clean, readable error logs.

---

## 5. Verification Plan

1. **Unit Verification**:
   - Verify `engine/credentials.py` resolves `OTTERLY_API_KEY` and handles stored credentials properly.
   - Run `python3 -m engine.otterly_client --help` to verify CLI argument parsing.
2. **Mock / Dry-Run Verification**:
   - Test `OtterlyClient` error handling with invalid key or non-existent brand report, verifying graceful fallback message.
3. **Pipeline Integration Test**:
   - Run `scripts/run_audit_pipeline.py --help` to verify flags (`--otterly-key`, `--no-otterly`).
   - Run a dry-run audit to verify fallback behavior when no Otterly report is present.
4. **Skill Packaging**:
   - Run `./package.sh` to package `.skill` bundle and verify synchronization with `~/.agents/skills/persuaid/`.
