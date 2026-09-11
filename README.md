# PersuAId — Executive Slide Deck Skill

**PersuAId** is a domain-agnostic agent skill for generating high-impact, persuasive executive presentation decks, GEO (Generative Engine Optimization) audits, and category strategy decks modeled after top-tier strategy consultancies (McKinsey, BCG) and specialized category intelligence reports.

## The 3-Step Process

```
┌───────────────────────────────────────────────────────────┐
│  STEP 1: The Deep Client Interview                        │
│  Extract core strategic context across 10 dimensions      │
└──────────────────────��──────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│  STEP 2: The Narrative Architecture                       │
│  Propose slide-by-slide arc using generalized archetypes  │
│  (Wait for user review, format choice, and approval)      │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│  STEP 3: Content Generation & Production                  │
│  Populate in-chat copy & generate zero-install HTML/PPTX  │
└────────────────────────────────────���──────────────────────┘
```

---

## 10 Core Dimensions (Step 1)

1. **Brand & Web Domain**: Brand name, domain URL, parent company backing.
2. **Location & Geographic Scope**: Country, primary metro hubs, high-growth corridors.
3. **Language & Category Lexicon**: Primary operating language, local dialects, English/industry loanwords.
4. **Target Audience Segments**: B2C retail consumers, home renovators, trade professionals (designers, architects).
5. **Named Persona Deep-Dive**: (e.g. *"The Home Improvement Planner"*, Age 25–45, seeking online inspiration, family safety, durability).
6. **Product Lines & SKU Tiering**: Premium vs entry-level lines, specialized formulations.
7. **Competitor Landscape**: Direct alternatives, competitor framing archetypes, market perception gaps.
8. **Customer Pain Points (Friction Spectrum)**: Aesthetic indecision, environmental failures (mold/stains), chemical odors, calculation uncertainty.
9. **Product USPs & The Moat**: Distinct sensory, technical, durability, and health/safety advantages.
10. **The 5-Stage Search & Buying Journey**: Discovery, Interest, Consideration, Purchase, After-Purchase across Google and AI engines (ChatGPT, Google AI Overviews, Perplexity, Copilot).

---

## Design System (Anti-Slop / Electrum DNA)

Generated decks follow a **locked visual system** extracted from the Electrum AI Visibility CONVR reference:

- Tokens: `references/design-theme.json` (accent `#3EC0C0`, pure black canvas)
- Rules: `references/anti-slop-rules.md`
- Locked shells: `references/slide-deck-code-templates.md` (slot-fill only)
- Prototype: `npm install && npm run golden` → `output/PersuAId_Golden_ElectrumDNA.pptx`

Client decks may override **accent + logos + cover photo** only — not layout geometry.

---

## Generalized Slide Archetypes Catalog (Step 2 & 3)

- **`ARCH-TITLE`**: High-contrast cover with scope metrics & metadata.
- **`ARCH-HERO-STAT`**: 4-metric grid highlighting core quantitative benchmarks + "What this means".
- **`ARCH-JOURNEY-MAP`**: 5-stage search journey overview (Discovery → Interest → Consideration → Purchase → After-Purchase).
- **`ARCH-JOURNEY-DEEPDIVE`**: Multi-engine prompt taxonomy matrix across journey stages.
- **`ARCH-TECH-AUDIT`**: On-Page Technical GEO & Authority Scorecard (Citability, Authority, E-E-A-T, Schema).
- **`ARCH-GAP-BAR`**: Ranked competitor share/gap bar visualization + driver breakdown.
- **`ARCH-SEGMENT-BREAKDOWN`**: 3-column breakdown across platforms, channels, or buyer tiers.
- **`ARCH-VOICE-GRID`**: Verbatim customer/AI quote cards exposing perceptual reality.
- **`ARCH-COMPETITOR-MATRIX`**: Multi-card positioning map detailing competitor archetypes vs Client.
- **`ARCH-MOAT-HIGHLIGHT`**: Unleveraged assets and proof points (scale metrics, network depth, partnerships).
- **`ARCH-SOURCE-MATRIX`**: Structured ecosystem table (`Source Type | In Data | Why It Matters | Lever`).
- **`ARCH-COMMUNITY-MAP`**: Direct buyer conversations and forum threads with status indicators (`🔴`, `🟡`, `🟢`).
- **`ARCH-RECOMMENDATION-SPLIT`**: 3-tier strategy blueprint (General, On-Page, Off-Page Media/Community).
- **`ARCH-PRIORITY-ACTION`**: 30-Day Priority Action sprint checklist vs 6-Month Phased Roadmap.
- **`ARCH-INVESTMENT`**: Commercial engagement tiers, commitment rules, and scope packages.
- **`ARCH-DELIVERABLES`**: Monthly itemized deliverables checklist with named content examples.
- **`ARCH-OPPORTUNITY-THESIS`**: Concluding executive manifesto affirming why the opportunity is ready to capture.

---

## Repository Structure

```
.
├── SKILL.md                          # Skill definition & 3-step execution rules
├── references/                       # On-demand reference documentation
│   ├── design-theme.json             # Locked Electrum DNA color/type/geometry tokens
│   ├── anti-slop-rules.md            # Visual production constraints
│   ├── slide-archetypes.md           # 17 slide archetypes & visual specs
│   ├── interview-framework.md        # 10-dimension deep client discovery engine
│   └── slide-deck-code-templates.md  # Locked pptxgenjs shells (slot-fill)
├── engine/                           # 🚀 Stealth Camoufox scraping & auth engine
│   ├── cli.py                        # CLI entry point (auth, audit, batch)
│   ├── models.py                     # Pydantic data models (AuditResult, Citation, AccountInfo)
│   ├── session_manager.py            # Account rotation & profile storage (profiles/)
│   └── drivers/                      # Stealth drivers (ChatGPT, Gemini)
├── scripts/                          # Zero-dependency Python automation utilities
│   ├── aggregate_metrics.py          # GEO audit aggregator (SoV, Win Rate, Funnels, Citations)
│   └── format_queries.py             # 5-stage search journey query generator
├── profiles/                         # 🍪 Session cookies & browser data (.gitignored)
├── pyproject.toml                    # Engine dependencies (camoufox, playwright, pydantic, typer, rich)
├── package.sh                        # Builds persuaid.skill for Claude Desktop / Web
└── README.md
```

---

## The All-in-One Automated GEO Pipeline (with `uv` or `python`)

You can run commands using [`uv`](https://github.com/astral-sh/uv) (recommended, zero-config virtualenv) or standard Python:

### 1. Interactive Authentication (Run once to persist cookies)
```bash
# Using uv:
uv run persuaid-geo auth --platform chatgpt --account acc1
uv run persuaid-geo auth --platform gemini --account acc1

# Or with python:
python3 -m engine.cli auth --platform chatgpt --account acc1
python3 -m engine.cli auth --platform gemini --account acc1
```

### 2. Generate 5-Stage Journey Queries (`scripts/format_queries.py`)
```bash
uv run scripts/format_queries.py \
  --brand "Samsung" \
  --category "foldable smartphones" \
  --competitors "OPPO,HONOR,Google Pixel" \
  --geo "Indonesia" \
  --out queries.json
```

### 3. Run Headless Stealth Audit (`engine/cli.py batch`)
```bash
# Using uv:
uv run persuaid-geo batch \
  --platform chatgpt \
  --file queries.json \
  --out results.json

# Or with python:
python3 -m engine.cli batch \
  --platform chatgpt \
  --file queries.json \
  --out results.json
```

### 4. Aggregate Metrics & Archetype Payloads (`scripts/aggregate_metrics.py`)
```bash
uv run scripts/aggregate_metrics.py \
  --file results.json \
  --brand "Samsung" \
  --out metrics.json
```

**Computed Metrics:**
- **AI Share of Voice (SoV) %**: Brand citation rate across queries.
- **#1 Recommendation Win Rate %**: Frequency of top organic recommendation.
- **5-Stage Search Journey Funnel**: Discovery, Interest, Consideration, Purchase, After-Purchase.
- **Top Competitor Presence**: Relative frequency of competitor mentions.
- **Citation Domain Classification**: Categorizes sources into *Editorial Tech Media*, *Community/Forums*, *Official Channels*, *Marketplaces*, and *Publishers*.

### 5. Generate Executive Presentation Deck (PersuAId Step 2 & 3)
PersuAId maps the computed `metrics.json` into its 17 modular slide archetypes, generating an in-chat structured presentation and a standalone `presentation.html` with a **1-click "📥 Export .PPTX" button** powered by client-side PptxGenJS (zero external CLI dependencies).

---

## Packaging for Claude Desktop / Claude Web

To package this skill as a `.skill` bundle for Claude Desktop or Claude Web:

```bash
./package.sh
```

This generates `dist/persuaid.skill`, bundling `SKILL.md`, `references/`, `scripts/`, and `engine/`.

---

## Testing Guide

### Test 1: Verify Engine Imports & CLI Help
```bash
python3 -m engine.cli --help
python3 scripts/format_queries.py --help
python3 scripts/aggregate_metrics.py --help
```

### Test 2: Interactive Auth & Single Headless Audit
```bash
# 1. Login once
python3 -m engine.cli auth --platform chatgpt --account acc1

# 2. Run single query headlessly
python3 -m engine.cli audit \
  --platform chatgpt \
  --query "What are the best foldable smartphones to buy in 2026?" \
  --brand "Samsung"
```

### Test 3: In Claude Desktop (Cowork Mode) / Claude Code
1. In Claude Desktop, link `red-persuaid-slide-deck` as a **Connected Folder** and select **Cowork** mode.
2. Prompt Claude:
   > *"Run an audit analysis on `results.json` using PersuAId and build an executive presentation deck for Samsung."*
3. Claude Cowork executes the aggregation script, designs the narrative architecture, and produces `presentation.html` with 1-click `.pptx` export.
