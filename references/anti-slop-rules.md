# PersuAId Anti-Slop Rules (Electrum DNA)

Locked visual policy for all generated decks. Content varies; **layout chrome and palette do not**.

## Design Read

Reading this as: **B2B consulting pitch deck** for C-suite, dark executive language, **single brand accent** on pure black — Electrum CONVR DNA.

## Hard Rules

1. **One accent hue** — default `#3EC0C0`. Client decks may swap accent only; do not invent a second decorative brand color.
2. **Semantic colors sparingly** — red/green/amber only for status or win/loss, never for decorating cards.
3. **Imagery** — text-led slides = solid black + type. Cover/section-break/closing CTA slides use `shellTitle` (`cover_motif` in `design-theme.json`): with a client photo, one real brand/product photo + dark gradient overlay + rounded search-bar pill wrapping the label — reused verbatim across the deck, never regenerated per slide, never AI-generated decorative art; without one, the shell's abstract-glow fallback (never flat black — see rule 12). Charts/tables/mockups = native shapes + text always.
4. **Locked chrome, alignment follows content density** — kicker (accent, ALL CAPS) → action title (two-tone: lead in `text`, punchline in `accent`, both bold, same line) → visual core → teal takeaway bar → footer (legal left, logos right). Center-align chrome for card-grid/quote-grid/synthesis archetypes; left-align chrome for chart/table/matrix archetypes (see `chrome.title_align_variants`) so the headline composes with the data instead of floating over it like a poster.
5. **Stroke cards, not filled rainbow cards** — thin accent border on dark fill; light quote cards only when archetype requires (e.g. voice grid).
6. **Typography** — Inter/Arial family only. Hierarchy via weight + color (white / muted / accent), not random sizes. Never render a full headline as one flat color/weight — always split lead vs. punchline per `typography.title_two_tone`.
7. **One job per slide** — no packing journey + matrix + roadmap onto one canvas.
8. **No repeated identical card-grid pattern across every archetype** — each shell must keep its own asymmetric composition (chart+sidebar, 60/40 split, 2×2 quote grid, icon-driver stack). Do not collapse every "4 things" into the same equal-width box row; that's the single most common AI-slop tell.
9. **Icon-anchored driver/insight lists** — sidebar and "why does this happen" lists use `addIconList` with one plain glyph from `theme.icons` per line, exactly like Electrum's own reference deck does. Plain-bullet walls of text are the thing to avoid (reads as a Word doc); a single ordinary icon leading each line is the fix — don't over-engineer it into a numbered badge or a hand-drawn vector shape, and don't stack more than one glyph per row.
10. **Takeaway lines stay punchy and separate** — `meansLines` render as short distinct sentences/lines (own visual beat), never comma/middle-dot-joined into one run-on paragraph.
11. **Forbidden defaults** — purple/indigo gradients, glass stacks, orange table headers, mesh hero backgrounds, emoji-as-pure-decoration (icons above are functional, not decorative), multi-accent metric grids (emerald+blue+red+amber).
12. **Cover/closing never flat black, and never a client-name kicker** — a title or closing CTA slide with no background treatment at all is a hard failure state; `shellTitle` must always paint either the photo motif or the abstract-glow fallback. The cover's accent kicker is a category tag (e.g. "GENERATIVE ENGINE OPTIMIZATION · EXECUTIVE BRIEFING"), never the bare client/brand name floating above the headline — the client already appears once, small, in the footer.
   - **The glow/photo background must never overlap the text.** Text on `shellTitle` occupies roughly `y: 1.6–5.2` at full width — check every decorative shape's bounding box (`y - d/2` to `y + d/2` etc.) against that band before placing it. A glow circle's edge cutting across headline letters happened before (positions chosen without this check) and is exactly the kind of self-inflicted overlap this rule exists to prevent — see the worked-safe positions in `addAbstractGlow`.
13. **Data-dense tables cap their own content, not just their layout** — `rowH` is a minimum, not a ceiling; a table shell (e.g. `ARCH-JOURNEY-MAP`) will silently grow past the safe area and overlap the footer if a cell is fed an unbounded list. Cap examples/bullets per cell (see each shell's own guidance) rather than relying on geometry to save you.

## Slot-Fill Contract

| Agent may change | Agent must NOT change |
|------------------|------------------------|
| Kicker / title / body copy | Safe margins, card sizes, footer Y |
| Metric values & labels | Background black / accent teal (unless client theme) |
| Table cell text | Column widths of locked shells |
| Brand name & logos | Inventing new archetype layouts mid-deck |

## QA Fingerprint (manual or scripted)

- Background ≈ pure black (`#000000` / `#0D1117`)
- Dominant non-neutral hue ≈ accent teal
- Kicker present, ALL CAPS, accent-colored
- Title has two distinct color/weight tones on the same line, not one flat run
- Chart/table/matrix slides are left-aligned; card-grid/quote slides are centered
- No two consecutive slides use the exact same equal-width N-box grid shape
- Takeaway bar present on analysis slides, with `meansLines` as separate short lines
- Footer legal + dual branding present
- No purple / orange-coral header bars
- Cover and closing slides have a painted background (photo or abstract-glow) — never flat black
- Cover kicker is a category tag, not the bare client name
- No table row/card visibly touches or crosses the footer line

See `design-theme.json` for numeric tokens and `slide-deck-code-templates.md` for locked shells.
