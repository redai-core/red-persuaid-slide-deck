# Slide Archetype Catalog

This catalog defines the generalized slide archetypes extracted from high-impact executive, GEO (Generative Engine Optimization), and strategic consulting decks (such as McKinsey SCR, BCG, and specialized AI visibility decks). Every slide is engineered with strict visual hierarchy: **Kicker Tag**, **Assertive Action Title**, **Visual Core (Cards/Charts/Grids/Tables)**, and an **Executive "What This Means" Synthesis Callout**.

---

## 1. Title / Cover Slide (`ARCH-TITLE`)
- **Visual Structure**: Minimalist, high-authority cover — real client photo + gradient when available, otherwise the shell's abstract-glow fallback. **Never a flat black background** — that reads as unfinished, not minimalist.
- **Components**:
  - Kicker: a **category tag**, e.g. `GENERATIVE ENGINE OPTIMIZATION · EXECUTIVE BRIEFING` — **not the bare client/brand name**. The client name is not a heading element on this slide; it already appears small in the footer (same as every other slide), so don't also float it as a standalone accent-colored line above the headline.
  - Headline: the assertive finding-as-thesis (2 lines), not a generic "[Client] GEO Audit" label.
  - Core Subtitle: the central thematic question or scope statement.
  - Optional scope-metrics row (3-4 key parameters, e.g. `71 prompts audited | 3 journey stages | 4 AI engines | 15 cities tracked`) — a small hero-stat strip *below* the subtitle, not instead of it.
  - Geography & Date metadata (e.g., `Market: Indonesia · Prepared by [Agency] · [Date]`).

---

## 2. Core Finding / Hero Stat Quad (`ARCH-HERO-STAT`)
- **Visual Structure**: 4-column metric grid or 2x2 hero card grid above a dual-column synthesis box.
- **Pitch Room Objective**: The Executive Wake-Up Call. Exposes the client's AI visibility blind spot despite strong legacy SEO investment.
- **Components**:
  - **Kicker**: `CORE FINDING` or `EXECUTIVE SUMMARY`
  - **Action Title**: Assertive takeaway (e.g., *"Dominant in traditional Google, but invisible to AI engines in 78% of high-intent prompts"*).
  - **Metric Grid (4 Cards)**:
    1. **Blended Share of Voice %**: Overall category visibility across tracked AI prompts (e.g., `14.2%` - *category presence*).
    2. **The Blind Spot Metric**: Lowest performing engine exposing vulnerability (e.g., `0.0%` - *visibility on Perplexity AI* or `12% vs 48%` *ChatGPT vs Gemini*).
    3. **#1 Recommendation Win Rate**: Frequency of holding the #1 top recommended spot (e.g., `8.5%` - *#1 rank share*).
    4. **Citation Market Share**: Share of total third-party citations owned vs rivals (e.g., `6.1%` - *of category citations*).
  - **"What this means" Callout**: High-contrast box clarifying that buyers are shifting to AI search where competitors currently own the default recommendation.

---

## 3. 5-Stage AI Search Journey Overview (`ARCH-JOURNEY-MAP`)
- **Visual Structure**: Full-width high-contrast structured table with **accent-teal** stroke/headers (`#3EC0C0` from `design-theme.json`; never orange/coral) and 5 clean stage row containers on a pure black background.
- **Components**:
  - **Kicker**: `SEARCH JOURNEY` or `AUDIENCE DISCOVERY`
  - **Action Title**: Narrative takeaway on the journey (e.g., *"Who we're reaching, and the journey we must own end-to-end"*)
  - **3-Column High-Contrast Table**:
    - **Column 1: `JOURNEY STAGE`** (Width: 20%): `1. Discovery`, `2. Interest`, `3. Consideration`, `4. Purchase`, `5. After purchase`.
    - **Column 2: `SEARCH INTENT`** (Width: 35%):
      - `1. Discovery`: *"Unbranded category, inspiration, problem-solving"*
      - `2. Interest`: *"Brand-specific, product lines, features & colors"*
      - `3. Consideration`: *"Brand/product comparison & reviews"*
      - `4. Purchase`: *"Purchase intent, local availability, pricing"*
      - `5. After purchase`: *"Application, maintenance, support & advocacy"*
    - **Column 3: `REPRESENTATIVE USER QUERIES / TOPICS`** (Width: 45%): 4-5 bulleted/quoted representative search queries per stage separated by middle dots (`·`) or line breaks.
  - **"What this means" Callout**: Pinpointing the exact journey stage where AI citations break down.

---

## 4. Complete Prompt Taxonomy Grid (`ARCH-JOURNEY-DEEPDIVE`)
- **Visual Structure**: 5-Card Container Grid arranged in 2 rows (3 cards in Top Row, 2 cards in Bottom Row) with dark stage header bars and clean white card bodies.
- **Components**:
  - **Kicker**: `QUERY TAXONOMY` or `PROMPT ECOSYSTEM`
  - **Action Title**: *"Prompt mapped to journey"*
  - **Subtitle**: `[Brand] [Category]` (e.g. *"Jotun Cat Interior"*, *"Electrum Motor Listrik"*)
  - **5-Card Container Grid**:
    - **Top Row (3 Cards)**:
      - **Card 1: `1 · DISCOVERY`**: Dark header bar + white card body with 8–10 authentic bulleted queries (`• cat interior terbaik`, `• warna cat ruang tamu 2026`, etc.).
      - **Card 2: `2 · INTEREST`**: Dark header bar + white card body with 8–10 authentic bulleted queries (`• Jotun cat interior`, `• katalog warna cat Jotun 2026`, etc.).
      - **Card 3: `3 · CONSIDERATION`**: Dark header bar + white card body with 8–10 authentic bulleted queries (`• Jotun vs Dulux interior`, `• review Jotun Majestic`, etc.).
    - **Bottom Row (2 Cards)**:
      - **Card 4: `4 · PURCHASE`**: Dark header bar + white card body with 8–10 authentic bulleted queries (`• harga cat Jotun interior`, `• toko cat Jotun terdekat`, etc.).
      - **Card 5: `5 · AFTER PURCHASE`**: Dark header bar + white card body with 8–10 authentic bulleted queries (`• cara menggunakan cat Jotun`, `• cara membersihkan noda di dinding`, etc.).
  - **Visual Detail**: Dark header rectangle (`#111827`) with bold white stage label; white card body (`#FFFFFF`) with dark text (`#111827`), crisp bullets, and subtle borders.

---

## 5. Technical GEO & Authority Audit (`ARCH-TECH-AUDIT`)
- **Visual Structure**: 2x3 scorecard grid with score badges, status indicators, and evaluation bullets.
- **Pitch Room Objective**: The "Smoking Gun" Technical Proof. Replaces subjective opinions with hard server log crawler data, proving the client's own tech stack is rejecting AI bots.
- **Components**:
  - **Kicker**: `ON-PAGE TECHNICAL AUDIT` or `THE SMOKING GUN`
  - **Action Title**: Audit conclusion (e.g., *"Your architecture is actively rejecting AI models: 58% of GPTBot crawl attempts fail"*).
  - **Audit Dimension Cards (6 Cards)**:
    1. **AI Bot Crawl Traffic**: Real crawl attempt volumes from server logs / Otterly Agent Stats (e.g., `GPTBot: 840 visits/mo | ClaudeBot: 310 visits/mo`).
    2. **Crawl Blockers & Render Walls**: Technical failure rate (e.g., `58% Blocked` - *client-side JS hydration timeout & 403 blocks*).
    3. **Robots.txt & AI Governance**: Crawl directive health (e.g., `Status: At Risk` - *PerplexityBot blocked; GPTBot throttled*).
    4. **Content E-E-A-T & Quotability**: Structural readiness for LLM extraction (e.g., `Quotable Snippets: 32/100 · Weak`).
    5. **Schema & Knowledge Graph**: Implementation of FAQSchema, MedicalEntity/ProductSchema, and Wikidata anchoring.
    6. **Platform Indexation Health**: Readiness across ChatGPT Search, Perplexity Sonar, and Google Gemini.
  - **"What this means" Callout**: Undeniable executive synthesis showing that fixing technical crawler accessibility is prerequisite to any marketing campaign.

---

## 6. Competitor Share / Gap Bar Chart (`ARCH-GAP-BAR`)
- **Visual Structure**: Horizontal bar chart on left with analytical driver cards on right.
- **Pitch Room Objective**: The Competitive Threat / FOMO. Demonstrates that rivals own the default recommendation and citation ecosystem.
- **Components**:
  - **Kicker**: `THE KEY GAP` or `MARKET SHARE DISTRIBUTION`
  - **Action Title**: Comparative verdict (e.g., *"[Competitor] has captured category mindshare — owning 52% of all AI citations"*).
  - **Ranked Horizontal Bars / Percentages**: Competitor citation share % vs Client share %, with average recommendation rank deltas.
  - **"Why does this happen?" Driver List**: 4 icon-anchored drivers explaining why competitors win (e.g., Structured schema dominance, third-party authority citations, dynamic rendering unblocked).
  - **"What this means" Callout**: Strategic imperative to reclaim category recommendation leadership before competitor moat deepens.

---

## 7. Breakdown by Platform / Engine / Segment (`ARCH-SEGMENT-BREAKDOWN`)
- **Visual Structure**: 3-column comparative cards comparing behavior across platforms or segments.
- **Components**:
  - **Kicker**: `COVERAGE BY ENGINE` or `PLATFORM SPLIT`
  - **Action Title**: Diagnosing root cause (e.g., *"Consistently low — a supply problem, not a platform problem"*)
  - **Platform Comparison Cards**: `ChatGPT` vs `Gemini` with visibility metrics, win rates, and citation sources.
  - **Analytical Takeaway Pair**: `⚠ Diagnostic Box` vs `✓ Single-Workstream Opportunity Box`.

---

## 8. Voice of Market / Verbatim Quotation Grid (`ARCH-VOICE-GRID`)
- **Visual Structure**: 4-card or 2x2 grid of direct AI quotes or customer verbatim snippets with giant quotation marks.
- **Components**:
  - **Kicker**: `POSITIONING` or `VOICE OF AI`
  - **Action Title**: Summary of perceptual reality (e.g., *"How AI describes Brand, in its own words"*)
  - **Quote Cards**: Verbatim quotes + source attribution.
  - **"What this means" Callout**: Synthesis explaining the perception mismatch.

---

## 9. Detailed Competitor Landscape Matrix (`ARCH-COMPETITOR-MATRIX`)
- **Visual Structure**: 5-column or vertical card split detailing competitor positioning archetypes.
- **Components**:
  - **Kicker**: `COMPETITOR LANDSCAPE`
  - **Action Title**: Structural market mapping (e.g., *"How each brand is framed — and where Client fits"*)
  - **Competitor Cards**: Name, positioning tag, market narrative, distribution strength, and Client card.

---

## 10. The Unleveraged Asset / Moat Highlight (`ARCH-MOAT-HIGHLIGHT`)
- **Visual Structure**: Left: 4 metric stats on niche dominance; Right: 3 strategic pillars of existing unfair advantages.
- **Components**:
  - **Kicker**: `THE ASSET YOU ALREADY HOLD` or `UNFAIR ADVANTAGES`
  - **Action Title**: Affirming latent strength (e.g., *"When Brand is named, it wins on infrastructure and quality"*).
  - **Niche Metric Stack + 3 Owned Asset Pillars**.

---

## 11. Source Base / Ecosystem Matrix (`ARCH-SOURCE-MATRIX`)
- **Visual Structure**: Structured executive data table with styled column badges.
- **Pitch Room Objective**: The Authority Ecosystem. Shows the client exactly where AI models get their facts—proving that on-page SEO is only half the battle.
- **Components**:
  - **Kicker**: `THE SOURCE BASE` or `CHANNEL ATTRIBUTION`
  - **Action Title**: Pinpointing citation drivers (e.g., *"Where AI answers originate: 4 authority hubs dictate 78% of citations"*).
  - **Table Columns / Top Cited Root Domains**: Leaderboard of top citation sources (`DOMAIN / SOURCE TYPE` | `CITATION FREQUENCY` | `CATEGORY ROLE` | `CLIENT ACTION LEVER`).
  - **"What this means" Callout**: Proving that winning AI search requires targeted seeding and co-citation on the specific 3-4 third-party authority portals that LLMs treat as canonical ground truth.

---

## 12. Community & Forum Opportunity Map (`ARCH-COMMUNITY-MAP`)
- **Visual Structure**: List of real-world buyer threads or decision venues with status badges.
- **Components**:
  - **Kicker**: `COMMUNITY THREAD MAP` or `BUYER CONVERSATIONS`
  - **Action Title**: Highlighting specific missing conversations.
  - **Opportunity Cards**: Sub-forum name, status badge (`🔴 Absent`, `🟡 Indirect`, `🟢 Dominant`), thread query, finding.

---

## 13. Strategic Recommendation Framework (`ARCH-RECOMMENDATION-SPLIT`)
- **Visual Structure**: 3-column strategic pillar layout: General, On-Page, Off-Page.
- **Components**:
  - **Kicker**: `STRATEGIC RECOMMENDATIONS` or `GEO BLUEPRINT`
  - **Action Title**: High-impact levers (e.g., *"Three coordinated workstreams to capture category recommendation share"*)
  - **3 Strategic Pillars**:
    1. `General Strategy`: Core positioning shift and target keyword cluster ownership.
    2. `On-Page Optimization`: Room calculators, comparison hubs, color guides, FAQ schema markup.
    3. `Off-Page Authority`: Tier-1 media reviews, publisher guidelines, Reddit/Kaskus community participation.
  - **"What this means" Callout**: Expected movement in AI visibility across 2 quarters.

---

## 14. Priority Action 30 Days & Phased Roadmap (`ARCH-PRIORITY-ACTION`)
- **Visual Structure**: Left side: 30-Day Sprint Checklist (Immediate Quick Wins); Right side: 6-Month Phased Roadmap.
- **Pitch Room Objective**: The Pitch Close / Retainer SOW. Bridges the gap between the identified problems and a billable engagement structure.
- **Components**:
  - **Kicker**: `ACTION PLAN` or `EXECUTION TRAJECTORY`
  - **Action Title**: Clear sequencing (e.g., *"30-day foundational sprint followed by 6-month scale"*)
  - **30-Day Sprint Box (Immediate Remediation Tickets)**: Injects concrete crawlability and schema fixes directly from audit findings (e.g. unblock GPTBot in Cloudflare CDN firewall, prerender core service pages, deploy JSON-LD FAQ/Service schema, claim entity authority).
  - **6-Month Phase Roadmap (3 Phases)**:
    - Phase 1 (Month 1-2): Foundation & On-Page Restructuring.
    - Phase 2 (Month 3-4): Community Authority & Citations Expansion.
    - Phase 3 (Month 5-6): Third-Party Media & Category Dominance.

---

## 15. Commercial Investment Scope (`ARCH-INVESTMENT`)
- **Visual Structure**: Side-by-side pricing & engagement package cards with feature checklists.
- **Components**:
  - **Kicker**: `RECOMMENDED ENGAGEMENT` or `INVESTMENT SCOPE`
  - **Action Title**: Commitment framework.
  - **Package Cards**: Workstream name, volume, duration, deliverables checklist `✓`.

---

## 16. Monthly Deliverables Specification (`ARCH-DELIVERABLES`)
- **Visual Structure**: 2-3 container cards with detailed checklist items and named examples.
- **Components**:
  - **Kicker**: `DELIVERABLES`
  - **Action Title**: Concrete certainty (e.g., *"What Client receives each month"*)
  - **Checklists**: Itemized bullet points with exact counts and named content assets.

---

## 17. Executive Opportunity Thesis / Concluding Vision (`ARCH-OPPORTUNITY-THESIS`)
- **Visual Structure**: Grand visual conclusion with large typography and core thesis.
- **Components**:
  - **Kicker**: `THE OPPORTUNITY` or `THE PATH FORWARD`
  - **Hero Affirmation**: Large bold statement (e.g., *"The market already knows you are real. It just doesn't tell buyers often enough."*)
  - **Synthesized Argument**: Crisp paragraph summarizing why the opportunity is ready to capture.
