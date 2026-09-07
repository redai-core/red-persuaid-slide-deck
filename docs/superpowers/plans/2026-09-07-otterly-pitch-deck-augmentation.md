# Otterly MCP Pitch Deck Augmentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Augment PersuAId slide deck skill with native, read-only Otterly.ai MCP intelligence to empower high-conviction C-suite sales pitch decks without changing existing slide layouts or canvas dimensions.

**Architecture:** Native In-Skill MCP Orchestration (Approach 1). When `mcp__otterly__*` tools exist, Step 1.5 searches for pre-configured brand reports under a strict zero-write policy, mapping bot crawl traffic, cross-engine blind spots, and citation market share into existing archetype slots, with zero-cost fallback to our ~18s Apify runner.

**Tech Stack:** Markdown / Agent Skill (`SKILL.md`, `references/slide-archetypes.md`), Bash packaging script (`package.sh`), PptxGenJS canvas.

---

### Task 1: Update `SKILL.md` with Version Bump and Otterly MCP Discovery & Safety Protocol

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Update Version Header and Mandatory Announcement**
Set version to `PersuAId v1.5.0 - Otterly Pitch Intelligence Active`.

- [ ] **Step 2: Update Step 1.5 with Otterly MCP Discovery and Read-Only Rules**
Add explicit rules:
- Environmental detection of `mcp__otterly__*` tools.
- Read-Only Whitelist: `list_workspaces`, `list_brand_reports`, `get_brand_report_stats`, `get_brand_report_agent_stats`, `list_brand_report_citations`, `list_brand_report_recommendations`.
- Strict Prohibited Tools (Never Call): `create_crawlability_check`, `create_content_check`, `create_query_fan_out`, `create_prompts`, `create_tag`, etc.
- Safe Fallback: If no matching pre-configured report exists for the brand, output notice and route seamlessly to the standard ~18s Apify pipeline.

- [ ] **Step 3: Update Step 2 Narrative Architecture with Pitch-First Framing**
Clarify that the deck is a consulting sales pitch deck designed to create urgency, deliver technical "smoking gun" proof, and sell the 30-day sprint and 6-month retainer.

- [ ] **Step 4: Commit changes**
```bash
git add SKILL.md
git commit -m "feat(skill): add Otterly MCP pitch intelligence and strict read-only safety gate (v1.5.0)"
```

---

### Task 2: Augment `references/slide-archetypes.md` with Pitch Proof Weapons

**Files:**
- Modify: `references/slide-archetypes.md`

- [ ] **Step 1: Augment `ARCH-HERO-STAT`**
Add Otterly cross-engine comparison data points (Blind spot metric, #1 recommendation win rate, citation market share).

- [ ] **Step 2: Augment `ARCH-TECH-AUDIT`**
Add the "Smoking Gun" proof slots: AI bot crawler stats (GPTBot / ClaudeBot visit volumes, JS hydration block %, robots.txt status).

- [ ] **Step 3: Augment `ARCH-GAP-BAR` & `ARCH-COMPETITOR-MATRIX`**
Add competitor citation market share and average recommendation rank deltas.

- [ ] **Step 4: Augment `ARCH-SOURCE-MATRIX` and `ARCH-PRIORITY-ACTION`**
Add real citation root domain leaderboard and injection of Otterly audit recommendations into the 30-day quick win sprint.

- [ ] **Step 5: Commit changes**
```bash
git add references/slide-archetypes.md
git commit -m "feat(archetypes): inject Otterly pitch proof points into slide archetypes"
```

---

### Task 3: Package and Synchronize Skill to Global Agent Directory

**Files:**
- Execute: `package.sh`
- Target: `dist/persuaid.skill` and `~/.agents/skills/persuaid/`

- [ ] **Step 1: Execute `package.sh`**
Run: `bash package.sh`
Expected: Successfully generates `dist/persuaid.skill` and copies all files to `~/.agents/skills/persuaid/`.

- [ ] **Step 2: Verify synchronization**
Verify that `~/.agents/skills/persuaid/SKILL.md` contains the v1.5.0 Otterly MCP instructions.

- [ ] **Step 3: Commit dist artifacts**
```bash
git add dist/persuaid.skill
git commit -m "chore: package and sync persuaid v1.5.0 skill bundle"
```

---

### Task 4: Update Persistent Project Memory

**Files:**
- Create: `/Users/dandydivaldy/.zcode/cli/memories/projects/red-persuaid-slide-deck-4b17e520a58f1589/memory/reference-otterly-ai-mcp.md`
- Modify: `/Users/dandydivaldy/.zcode/cli/memories/projects/red-persuaid-slide-deck-4b17e520a58f1589/memory/MEMORY.md`

- [ ] **Step 1: Write `reference-otterly-ai-mcp.md`**
Document Otterly MCP tool capabilities, strict read-only whitelist, pitch deck proof points, and Apify fallback.

- [ ] **Step 2: Update `MEMORY.md`**
Add pointer line for Otterly AI MCP reference.
