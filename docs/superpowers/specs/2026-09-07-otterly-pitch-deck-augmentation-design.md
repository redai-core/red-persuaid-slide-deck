# Design Spec: Otterly.ai MCP Pitch Deck Augmentation for PersuAId

- **Date:** 2026-09-07
- **Target Skill:** `persuaid` (Base: `~/.agents/skills/persuaid/`, Repo: `SKILL.md`)
- **Version Bump:** `PersuAId v1.5.0 - Otterly Pitch Intelligence`
- **Scope:** Native In-Skill Read-Only MCP Orchestration (Approach 1)

---

## 1. Executive Context & Objective

The primary deliverable of PersuAId is an **executive sales / consulting pitch deck** (16:9 HD `.pptx` + structured copy), designed to persuade C-suite buyers and prospects why they urgently need Generative Engine Optimization (GEO) services and retainers.

**It is NOT an exhaustive technical report dump.** The slide deck's job in a pitch room is to:
1. **Create Urgency / Wake-Up Call:** Expose where the prospect is losing high-intent AI search traffic to competitors across ChatGPT, Perplexity, and Gemini.
2. **Deliver the "Smoking Gun" Technical Proof:** Provide indisputable evidence that the client's current site architecture is actively blocking or failing AI search crawlers.
3. **Sell the Solution:** Map concrete 30-day quick wins and a 6-month GEO retainer that resolves the gap.

### Key Constraint
**Do NOT change the existing slide deck landscape, visual layout, or 16:9 HD canvas.** The modular archetypes (`ARCH-TITLE`, `ARCH-HERO-STAT`, `ARCH-JOURNEY-MAP`, `ARCH-JOURNEY-DEEPDIVE`, `ARCH-TECH-AUDIT`, `ARCH-GAP-BAR`, `ARCH-SOURCE-MATRIX`, `ARCH-PRIORITY-ACTION`) remain 100% intact. Otterly.ai MCP data is strictly used to **augment the content inside the existing archetype slots** to make the pitch hit with maximum conviction.

---

## 2. Strict Read-Only Safety Protocol (Option 1)

To protect client credits and prevent accidental billing from autonomous tool loops, the integration enforces a **strict read-only gate on pre-configured workspaces**.

### 2.1 Authorized Tools (Read-Only Whitelist)
Only the following tools may be invoked if present in the environment:
* `mcp__otterly__list_workspaces`
* `mcp__otterly__list_brand_reports`
* `mcp__otterly__get_brand_report_stats`
* `mcp__otterly__get_brand_report_agent_stats`
* `mcp__otterly__list_brand_report_citations`
* `mcp__otterly__list_brand_report_recommendations`

### 2.2 Strictly Prohibited Tools (Zero-Write Enforcement)
The agent is explicitly forbidden from calling any write or creation tools:
* ❌ `mcp__otterly__create_crawlability_check`
* ❌ `mcp__otterly__create_content_check`
* ❌ `mcp__otterly__create_query_fan_out`
* ❌ `mcp__otterly__create_prompts`
* ❌ `mcp__otterly__delete_prompt`
* ❌ `mcp__otterly__create_tag` / `update_prompt_tags` / `delete_tag`

### 2.3 Discovery & Fallback Flow
1. **Detection:** At Step 1.5, the skill checks for `mcp__otterly__*` tools.
2. **Lookup:** If available, it executes `list_brand_reports()` to search for the brand name or domain provided in Step 1.
3. **Match Found:** Retrieves `reportId` and pulls read-only stats (`get_brand_report_stats`, `get_brand_report_agent_stats`, `list_brand_report_citations`, `list_brand_report_recommendations`).
4. **No Match Found:** If no matching report exists, the agent outputs:
   > `[Otterly MCP: No pre-configured report found for '{brand}'. Preserving credits and proceeding with standard live Apify audit.]`
   It immediately routes to the standard ~18s Apify runner. It **never** creates a new report or tests URLs on Otterly autonomously.

---

## 3. Data Mapping into Pitch Slide Archetypes

| Slide Archetype | Standard Baseline (Apify) | Augmented with Otterly MCP Data | Pitch Room Impact |
| :--- | :--- | :--- | :--- |
| **`ARCH-HERO-STAT`** *(Executive Wake-Up Call)* | 4 sample KPI cards from 10-query snapshot | Cross-engine comparison (`get_brand_report_stats`): Blended SoV %, Lowest-engine blind spot (e.g. Perplexity 0% vs Gemini 42%), #1 Win Rate %, Citation Share % | Exposes the blind spot: *"You dominate traditional SEO, but are invisible on Perplexity & ChatGPT."* |
| **`ARCH-TECH-AUDIT`** *(The "Smoking Gun")* | Heuristic rule-based scorecard (Good/Fair/Poor) | Real AI crawler server log data (`get_brand_report_agent_stats`): GPTBot / ClaudeBot visit volumes, % requests blocked by JS hydration / 403s, robots.txt status | Undeniable proof: *"AI bots tried to crawl your site 800+ times last month, but 58% failed due to client-side JS."* |
| **`ARCH-GAP-BAR` & `ARCH-COMPETITOR-MATRIX`** *(The Threat)* | Modeled competitor share bars | Empirical competitor citation share % and average recommendation rank delta | FOMO / Urgency: *"Competitor A captures 4.2x more AI citations in your core service lines."* |
| **`ARCH-SOURCE-MATRIX`** *(Authority Map)* | Generic category breakdown (News, Portals) | Leaderboard of top 5 specific citation root domains driving AI answers (`list_brand_report_citations`) | Ecosystem clarity: *"Winning ChatGPT requires seeding these 3 specific portals that AI models treat as source truth."* |
| **`ARCH-PRIORITY-ACTION`** *(The Retainer SOW)* | General 30-day quick wins vs 6-month roadmap | Direct injection of Otterly audit recommendations (`list_brand_report_recommendations`) into 30-day tickets | High-conviction close: Direct line from identified crawl blockers to billable sprint deliverables. |

---

## 4. Skill Versioning & Response Discipline

1. **Version Tag:** When initialized, the skill announces its active version:
   `[PersuAId v1.5.0 - Otterly Pitch Intelligence Active]`
2. **Visual Consistency:** Presentation code continues to use modern 16:9 HD canvas (`13.333" × 7.5"`), `LAYOUT_16_9_HD`, and standardized safe coordinates (`SAFE_X = 0.8`, `SAFE_W = 11.733`).
3. **Packaging:** Changes apply to `SKILL.md`, `references/`, and sync via `package.sh` directly into `~/.agents/skills/persuaid/`.
