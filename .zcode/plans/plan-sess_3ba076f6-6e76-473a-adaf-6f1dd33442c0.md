# Strategic Enrichment Plan for PersuAId Skill

## 1. Context & Scope
Based on the GEO (Generative Engine Optimization) brief, we are enhancing PersuAId to seamlessly handle advanced category intelligence, technical audits, and consumer search journeys while keeping the skill 100% domain-agnostic and excluding automated backend scraping/predictive engines for now.

---

## 2. Key Enhancements Planned

### A. Deep Client Interview (Step 1) — Expanded to 10 Dimensions
We will upgrade the interview engine in `references/interview-framework.md` and `SKILL.md` to capture:
1. **Domain & Brand Identity**: Brand name, parent backing, primary web domain.
2. **Target Geography & Regional Focus**: Major metro markets, high-growth residential/commercial zones.
3. **Language & Industry Lexicon**: Primary operating language, local dialect nuances, and common English/industry loanwords (e.g. "low odor", "E-E-A-T", "matt finish").
4. **Target Audience Segments**: Broad audience split (B2C consumers, young families, renovators, trade professionals like architects/interior designers).
5. **Named Persona Deep-Dive**: Specific archetype profile (e.g. "The Home Improvement Planner", Age 25–45, seeking online inspiration, family safety, durability).
6. **Product Lines & Tiering**: Flagship sub-brands and SKU tiers (e.g. premium vs entry-level lines).
7. **Competitor Landscape**: Direct alternatives, market tiering, and category incumbents.
8. **Deep Customer Pain Points**: Multi-layered frictions (aesthetic indecision, spatial visualization, durability/maintenance, safety/chemical anxiety, calculation friction).
9. **Product USPs & Moat**: Distinct sensory, technical, durability, and health/safety advantages.
10. **The 5-Stage Search & Buying Journey**: Mapping how buyers search across Google & AI engines (ChatGPT, Google AI Overviews, Perplexity, Copilot) across 5 stages:
    - *Discovery* (Category & broad inspiration queries)
    - *Interest* (Brand product queries, catalogs, price checks)
    - *Consideration* (Brand vs Competitor comparisons, reviews, sub-brand choices)
    - *Purchase* (Nearby store finders, official online stores, volume calculators, promos)
    - *After-Purchase* (Application guides, maintenance, stain removal, troubleshooting)

---

### B. Slide Archetype Catalog (Step 2 & 3) — New Strategic Archetypes
We will add 4 new modular archetypes to `references/slide-archetypes.md`:
1. `ARCH-JOURNEY-MAP` / `ARCH-QUERY-MATRIX`:
   - High-level 5-stage search journey overview and deep-dive query breakdown across AI platforms (ChatGPT, Google AI Overviews, Perplexity, Copilot).
2. `ARCH-TECH-AUDIT`:
   - On-Page Technical GEO & Authority Scorecard (AI Citability Score, Brand Authority, Content E-E-A-T, Schema & Structured Data, Platform Optimization, Overall Score).
3. `ARCH-RECOMMENDATION-SPLIT`:
   - Strategic 3-tier recommendation framework: *General Strategy*, *On-Page Optimization* (Guides, calculators, FAQs), and *Off-Page Authority* (Editorial PR, forums/communities, publisher guidelines).
4. `ARCH-PRIORITY-ACTION`:
   - 30-Day Priority Action Quick-Wins vs 6-Month Phased Roadmap.

---

### C. Zero-Dependency HTML/PPTX Export Boilerplate
Update `references/slide-deck-code-templates.md` to ensure the new journey matrix and scorecard archetypes render cleanly in the single-file interactive HTML viewer and export smoothly to `.pptx`.

---

## 3. Files to Update
1. `SKILL.md` (Update Step 1 dimensions, Step 2 archetypes, Step 3 formatting)
2. `references/interview-framework.md` (Detailed 10-dimension interview questions & prompt taxonomy)
3. `references/slide-archetypes.md` (Add Journey Map, Tech Scorecard, 30-Day Action archetypes)
4. `references/slide-deck-code-templates.md` (HTML & PPTX layout snippets for new archetypes)
5. `README.md` (Updated documentation)
6. Sync to `~/.agents/skills/persuaid/`, run `./package.sh`, and commit to git (no remote push).