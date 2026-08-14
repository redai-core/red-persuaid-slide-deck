# PersuAId — Executive Slide Deck Skill

**PersuAId** is a domain-agnostic agent skill for generating high-impact, persuasive executive presentation decks modeled after top-tier strategy consultancies (McKinsey, BCG) and specialized category intelligence reports.

## The 3-Step Process

```
┌───────────────────────────────────────────────────────────┐
│  STEP 1: The Deep Client Interview                        │
│  Extract core strategic context across 7 dimensions       │
└───────────────────────���─────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│  STEP 2: The Narrative Architecture                       │
│  Propose slide-by-slide arc using generalized archetypes  │
│  (Wait for user review and explicit approval)             │
└─────────────────────────────┬─────────────────────────────┘
                              ▼
┌───────────────────────────────────────────────────────────┐
│  STEP 3: Content Generation & Production                  │
│  Populate client-ready copy, data specs & deliverables    │
└───────────────────────────────────────────────────────────┘
```

---

## 7 Core Dimensions (Step 1)

1. **Brand & Location**: Brand name, domain URL, parent/holding company, target geography.
2. **Audience & Persona**: Primary decision-makers, ICP, buyer vs user personas.
3. **Product & USP**: Core offerings, flagship tiers, proprietary moat/unfair advantage.
4. **Competitor Landscape**: Primary direct alternatives, competitor framing archetypes, market perception gap.
5. **Customer Pain Points**: Frustrations with alternatives, friction points in adoption.
6. **Primary Need & JTBD**: Ultimate functional, emotional, and business payoff desired by the customer.
7. **Search / Buying Behavior**: How buyers discover, evaluate, compare, and validate solutions.

---

## Generalized Slide Archetypes Catalog (Step 2 & 3)

- **`ARCH-TITLE`**: High-contrast cover with scope metrics & metadata.
- **`ARCH-HERO-STAT`**: 4-metric grid highlighting core quantitative benchmarks + "What this means".
- **`ARCH-GAP-BAR`**: Ranked competitor share/gap bar visualization + driver breakdown.
- **`ARCH-SEGMENT-BREAKDOWN`**: 3-column breakdown across platforms, channels, or buyer tiers.
- **`ARCH-VOICE-GRID`**: Verbatim customer/AI quote cards exposing perceptual reality.
- **`ARCH-COMPETITOR-MATRIX`**: Multi-card positioning map detailing competitor archetypes vs Client.
- **`ARCH-MOAT-HIGHLIGHT`**: Unleveraged assets and proof points (scale metrics, network depth, partnerships).
- **`ARCH-SOURCE-MATRIX`**: Structured ecosystem table (`Source Type | In Data | Why It Matters | Lever`).
- **`ARCH-COMMUNITY-MAP`**: Direct buyer conversations and forum threads with status indicators (`🔴`, `🟡`, `🟢`).
- **`ARCH-ACTION-PLAN`**: 3-phase strategic roadmap cards with clear `Maps to:` rationales.
- **`ARCH-ENABLERS`**: 4 operational pillars (Daily Tracking, Discovery, Competitor Intel, Monthly Reviews).
- **`ARCH-INVESTMENT`**: Commercial engagement tiers, commitment rules, and scope packages.
- **`ARCH-DELIVERABLES`**: Monthly itemized deliverables checklist with named content examples.
- **`ARCH-OPPORTUNITY-THESIS`**: Concluding executive manifesto affirming why the opportunity is ready to capture.

---

## Repository Structure

```
.
├── SKILL.md                          # Skill definition & 3-step execution rules
├── references/                       # On-demand reference documentation
│   ├── slide-archetypes.md           # 14 slide archetypes & visual specs
│   ├── interview-framework.md        # 7-dimension deep client discovery engine
│   └── slide-deck-code-templates.md  # Single-file HTML/Tailwind & Marp boilerplates
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
