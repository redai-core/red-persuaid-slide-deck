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
│   ├── slide-archetypes.md           # 17 slide archetypes & visual specs
│   ├── interview-framework.md        # 10-dimension deep client discovery engine
│   └── slide-deck-code-templates.md  # Single-file HTML with 1-click PPTX export & Marp templates
├── package.sh                        # Builds persuaid.skill for Claude Desktop / Web
└── README.md
```

---

## Packaging for Claude Desktop / Claude Web

To package this skill as a `.skill` bundle for Claude Desktop or Claude Web:

```bash
./package.sh
```

This generates `dist/persuaid.skill`, which can be imported directly into Claude.
