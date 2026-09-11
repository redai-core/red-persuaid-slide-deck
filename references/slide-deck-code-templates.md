# Slide Deck Code & Generation Templates

PersuAId generates native **16:9 HD** (`13.333" × 7.5"`) decks with **pptxgenjs**.

**Visual source of truth:** `references/design-theme.json` + `references/anti-slop-rules.md`  
**Layout rule:** LLM fills **content slots only**. Geometry, chrome, and palette stay locked (Electrum DNA).

Golden prototype: `node scripts/generate_golden_deck.mjs`  
Reference deck (full shells in use): `node scripts/generate_auto2000_deck.mjs`

### Shell inventory

| Archetype | In this doc | In Auto2000 script |
|-----------|:-----------:|:------------------:|
| `ARCH-TITLE` / `ARCH-TITLE-PHOTO` | ✓ | ✓ (title) |
| `ARCH-HERO-STAT` | ✓ | ✓ |
| `ARCH-COMPARE-SPLIT` | ✓ | — |
| `ARCH-JOURNEY-MAP` | ✓ | ✓ |
| `ARCH-GAP-BAR` | ✓ | ✓ |
| `ARCH-SOURCE-MATRIX` | ✓ | ✓ |
| `ARCH-TECH-AUDIT` | ✓ | ✓ |
| `ARCH-VOICE-GRID` | ✓ | ✓ |
| `ARCH-RECOMMENDATION-SPLIT` | ✓ | ✓ |
| `ARCH-PRIORITY-ACTION` | ✓ | ✓ |
| Remaining catalog (`JOURNEY-DEEPDIVE`, `SEGMENT-BREAKDOWN`, …) | — | — |

---

## Theme constants (do not freestyle)

```javascript
import pptxgen from "pptxgenjs";
import theme from "../references/design-theme.json" with { type: "json" };

const C = theme.colors;
const FONT = theme.typography.body; // Arial — portable; Inter when embedded
const SAFE_X = theme.canvas.safe_x_in;
const SAFE_W = theme.canvas.safe_w_in;

// The footer sits at y=7.08. NOTHING below this file — no box, no text, no table row, no
// takeaway bar — may cross this line on ANY slide. Every shell below that sizes a box or
// computes item spacing from a variable-length list (recommendations, phases, sidebar notes,
// table rows) must clamp its geometry against this constant. This is not optional per-shell
// scaffolding — define it once, here, at the top of every generation script, or a shell that
// references it (e.g. `ARCH-PRIORITY-ACTION`) will throw/compute NaN and silently blow past the
// footer instead of the safety clamp actually running.
const FOOTER_SAFE_Y = 6.98;
```

When a client brand kit supplies an accent hex, override `C.accent` / `C.stroke` / `C.accent_banner` only. Keep blacks and greys.

---

## Locked chrome helpers

`addChrome` takes an explicit `align` ("center" for card-grid/quote archetypes, "left" for chart/table/matrix archetypes — see `chrome.title_align_variants`) and renders the title as **two color tones on one line** (lead + punchline) instead of one flat run. Pass `title` as a string (auto-splits at the last comma/dash, or first `**...**` marker) or as `{ lead, emphasis }` for explicit control.

```javascript
function splitTitleTones(title) {
  if (typeof title === "object") return title;
  // Explicit split marker: "Lead text|Emphasis punchline"
  if (title.includes("|")) {
    const [lead, emphasis] = title.split("|");
    return { lead: lead.trim() + " ", emphasis: emphasis.trim() };
  }
  return { lead: title, emphasis: "" };
}

/** Electrum's actual footer lockup is "[Redcomm R. mark] | [client wordmark]" — a real agency
 * logo image, never the client name floating alone as plain text (that read as a stray label,
 * not branding). The Redcomm mark is a fixed asset (`assets/redcomm_logo_white.png`, extracted
 * from the reference deck: white "R." on transparent, 99×145px, aspect ratio locked at 145/99).
 * Client identity is still just text (`client`) unless/until a client logo asset is supplied —
 * do not invent or fetch a client logo image. */
function addFooterBranding(slide, { client = "Client", logoPath = "assets/redcomm_logo_white.png" } = {}) {
  const logoH = 0.22;
  const logoW = logoH * (99 / 145);
  const footerY = 7.04;
  const rightEdge = SAFE_X + SAFE_W;
  const clientW = 1.7;
  const dividerW = 0.14;
  const gap = 0.1;
  const totalW = logoW + gap + dividerW + gap + clientW;
  const startX = rightEdge - totalW;
  slide.addImage({ path: logoPath, x: startX, y: footerY, w: logoW, h: logoH });
  slide.addText("|", {
    x: startX + logoW + gap, y: footerY - 0.03, w: dividerW, h: logoH + 0.06,
    fontSize: 13, color: C.text_dim, fontFace: FONT, align: "center", valign: "middle",
  });
  slide.addText(client.toLowerCase(), {
    x: startX + logoW + gap + dividerW + gap, y: footerY - 0.02, w: clientW, h: logoH + 0.04,
    fontSize: 11, bold: true, color: C.text, fontFace: FONT, valign: "middle",
  });
}

function addChrome(slide, { kicker, title, align = "center", agency = "Redcomm Indonesia", client = "Client", year = 2026 }) {
  slide.background = { color: C.bg };

  slide.addText(kicker.toUpperCase(), {
    x: SAFE_X, y: 0.32, w: SAFE_W, h: 0.28,
    fontSize: 11, bold: true, color: C.accent, fontFace: FONT, align,
  });

  const { lead, emphasis } = splitTitleTones(title);
  const titleRuns = [{ text: lead, options: { color: C.text, bold: true } }];
  if (emphasis) titleRuns.push({ text: emphasis, options: { color: C.accent, bold: true } });
  slide.addText(titleRuns, {
    x: SAFE_X, y: 0.62, w: SAFE_W, h: 0.7,
    fontSize: 24, fontFace: FONT, align,
  });

  slide.addText(`${agency}  ·  © ${year}. All Rights Reserved. Confidential Do Not Distribute.`, {
    x: SAFE_X, y: 7.08, w: 7.5, h: 0.25,
    fontSize: 8, color: C.text_dim, fontFace: FONT,
  });

  addFooterBranding(slide, { client });
}

/** Dual takeaway pattern from Electrum: dark insight strip + bright accent bar.
 * meansLines render as separate short lines (own visual beat), never joined into one run-on sentence.
 * The caller's `y` comes from wherever the visual core above happens to end — a table with more
 * rows than expected, an extra metric card row, etc. can easily push that past a safe value, so
 * this function clamps itself against FOOTER_SAFE_Y rather than trusting the caller. This is the
 * actual fix for the recurring "table/roadmap text crosses the footer" bug — apply it here, not
 * only in the one shell that happened to get caught red-handed last time. */
function addTakeawayStack(slide, { insightLines, meansLines, y = 5.35 }) {
  const insightH = 0.72;
  const th = 0.85;
  const stackH = insightH + 0.1 + th;
  if (y + stackH > FOOTER_SAFE_Y) y = FOOTER_SAFE_Y - stackH;
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: SAFE_X, y, w: SAFE_W, h: insightH,
    fill: { color: C.bg_insight }, line: { color: C.stroke_muted, width: 1 }, rectRadius: 0.06,
  });
  slide.addText(insightLines.join("\n"), {
    x: SAFE_X + 0.25, y: y + 0.1, w: SAFE_W - 0.5, h: insightH - 0.18,
    fontSize: 11, color: C.text, fontFace: FONT, align: "center",
  });

  const ty = y + insightH + 0.1;
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: SAFE_X, y: ty, w: SAFE_W, h: th,
    fill: { color: C.accent_banner }, line: { color: C.accent_banner, width: 0 }, rectRadius: 0.06,
  });
  const meansBody = [
    { text: "What this means:\n", options: { bold: true, color: C.text_on_accent } },
    ...meansLines.flatMap((line, i) => [
      { text: line, options: { color: C.text_on_accent } },
      { text: i < meansLines.length - 1 ? "\n" : "", options: {} },
    ]),
  ];
  slide.addText(meansBody, {
    x: SAFE_X + 0.3, y: ty + 0.1, w: SAFE_W - 0.6, h: th - 0.2,
    fontSize: 11.5, fontFace: FONT, align: "center", valign: "middle", lineSpacingMultiple: 1.05,
  });
}

/** Icon-anchored driver/insight list — Electrum's own "Why does this happen?" sidebar pattern
 * (see the reference deck: 📰💬🌐⚡🧠✓🤝). Electrum uses ordinary single-glyph icons directly —
 * not a numbered badge, not a hand-drawn vector primitive. Match that: one plain icon glyph from
 * `theme.icons` per line, modestly sized, never more than one per row, never purely decorative. */
// Each card's height is derived from its own text length — a fixed cardH sized for ~2 lines
// silently overflows into the next card the moment an item's text wraps to 3 lines (which real
// content regularly does). That overflow — one card's text visibly overlapping the card below it
// — is exactly the bug this replaces. `minCardH`/`gap` are floors, not fixed values.
//
// `estimateIconListHeight` runs the identical line-wrap estimate WITHOUT drawing anything, so a
// caller can size the containing sidebar/box correctly before it draws that box (the box has to
// be drawn first, underneath the cards — you cannot size it from addIconList's return value,
// which only exists after the cards are already on the slide). Keep the two estimates in sync.
function estimateIconListHeight(items, w, { minCardH = 0.6, gap = 0.12, fontSize = 11 } = {}) {
  const textW = w - 0.95;
  const charsPerLine = Math.max(10, Math.floor(textW * 12.5 * (11 / fontSize)));
  const lineH = (fontSize / 72) * 1.35;
  let total = 0;
  items.forEach((item) => {
    const lines = Math.max(1, Math.ceil(item.text.length / charsPerLine));
    total += Math.max(minCardH, lines * lineH + 0.24) + gap;
  });
  return total - gap; // no trailing gap after the last card
}

function addIconList(slide, { x, y, w, items, minCardH = 0.6, gap = 0.12, dark = true, fontSize = 11 }) {
  const textW = w - 0.95; // available width for item.text after the icon column
  const charsPerLine = Math.max(10, Math.floor(textW * 12.5 * (11 / fontSize))); // rough but conservative Arial-bold estimate
  const lineH = (fontSize / 72) * 1.35;
  let iy = y;
  items.forEach((item) => {
    const lines = Math.max(1, Math.ceil(item.text.length / charsPerLine));
    const cardH = Math.max(minCardH, lines * lineH + 0.24);
    slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x, y: iy, w, h: cardH,
      fill: { color: dark ? C.card_light : C.bg }, line: { width: dark ? 0 : 1.25, color: C.stroke },
      rectRadius: 0.06,
    });
    slide.addText(item.icon || "", {
      x: x + 0.15, y: iy + 0.08, w: 0.5, h: cardH - 0.16,
      fontSize: 18, align: "center", valign: "middle",
    });
    slide.addText(item.text, {
      x: x + 0.75, y: iy + 0.08, w: textW, h: cardH - 0.16,
      fontSize, bold: true, color: dark ? C.card_light_text : C.text, fontFace: FONT, valign: "middle",
    });
    iy += cardH + gap;
  });
  return iy - gap; // bottom y of the last card — use this to size/validate the containing sidebar box
}
```

---

## Shell: `ARCH-TITLE` / `ARCH-TITLE-PHOTO` (cover, section break, closing CTA)

**One shell, two backgrounds — never a flat black cover.** A flat-black title/closing slide is a hard failure state (it reads as unfinished), so this shell always paints a background:
- `photoPath` supplied → Electrum's real cover-photo motif (photo + left-to-right dark gradient).
- No `photoPath` → automatic **abstract glow fallback** (dark navy base + 3 large soft translucent accent circles, drawn from native shapes). Never omit this fallback — it is the default path for most decks (no client photo on hand) and must still look art-directed, not placeholder.

**No client/brand name as a kicker.** The old pattern of printing the client name in accent color above the headline (e.g. a lone `"auto2000"` floating over the cover) is a bug, not a feature — it reads as a stray label, not a deliberate design element. The client name appears once, small, in the footer's bottom-right corner (handled by every other locked-chrome slide) — that is enough branding. Use `kicker` on the cover for a **category tag** instead (e.g. `"GENERATIVE ENGINE OPTIMIZATION · EXECUTIVE BRIEFING"`), never the brand name.

**Slots:** `variant` (`"cover"` | `"divider"` | `"closing"` — cover/closing render a two-line headline + optional subtitle; divider renders Electrum's rounded pill wrapping a short label like `"BRAND REPORT"` / `"APPENDIX"`), `kicker` (category tag, cover/closing only), `headline` / `label`, `subtitle`, `photoPath` (optional), `footerNote` (optional override for the standard agency/copyright line — use for a closing slide's contact line), `agency`, `client`

```javascript
// Text-safe zone for cover/divider/closing content is roughly y:1.6–5.2 (kicker → subtitle),
// full width. Every glow circle's bounding box must stay OUTSIDE that band — confine them to the
// top strip only (y_max ≤ 1.55), never spanning down into where the headline/subtitle sit. A
// previous version placed circles at y:-2/3.6/4.8 with d up to 7.5 — their edges cut straight
// through the headline text. Check new positions against this rule before ever changing them.
// Safe zones on a shellTitle slide: top band y ≤ 1.55 (above the kicker), bottom band
// y 5.3–6.9 (below the subtitle, above the footer), full width. Every shape below is checked
// against one of those two bands — never the y:1.6–5.2 text band, never y ≥ 6.98.
function addAbstractGlow(s) {
  s.background = { color: "0A1420" };

  // Corner glows. Each circle's CENTER sits near (not on) the actual slide corner, so a real,
  // proportionate arc bleeds into the canvas — a circle centered many inches outside the canvas
  // (an earlier version) only ever shows a paper-thin sliver at the very edge, which reads as a
  // rendering glitch, not a deliberate glow. Still hard-constrained to the safe bands: top
  // circles' bottom edge ≤ 1.55 (above the kicker), bottom circles' top edge ≥ 5.3 (below the
  // subtitle) — verify `y (box top) + d` / `y (box top)` against those before changing values.
  [
    { x: -2.1, y: -2.1, d: 3.0, color: C.accent, trans: 82 },        // top-left,  center (-0.6,-0.6), y max = 0.9
    { x: 12.433, y: -2.1, d: 3.0, color: C.accent_deep, trans: 84 }, // top-right, center (13.9,-0.6), y max = 0.9
    { x: -0.8, y: 5.7, d: 2.4, color: C.accent_deep, trans: 86 },    // bottom-left,  center (0.4,6.9), y min = 5.7
    { x: 11.733, y: 5.7, d: 2.4, color: C.accent, trans: 87 },       // bottom-right, center (12.9,6.9), y min = 5.7
  ].forEach((g) => {
    s.addShape(pptx.shapes.OVAL, {
      x: g.x, y: g.y, w: g.d, h: g.d,
      fill: { color: g.color, transparency: g.trans }, line: { width: 0 },
    });
  });

  // Thin stroke-only ring for depth, top-right — an orbit accent, not a filled blob.
  s.addShape(pptx.shapes.OVAL, {
    x: 8.5, y: -6.5, w: 8.5, h: 8.5,
    fill: { type: "none" }, line: { color: C.accent, width: 1, transparency: 75 },
  });

  // A handful of small "network node" dots, top band only — echoes the GEO/AI subject matter
  // without reading as random clip-art (they're plain filled circles, one accent hue, no icons).
  [
    { x: 2.4, y: 0.55, d: 0.09 }, { x: 5.1, y: 0.3, d: 0.06 }, { x: 7.8, y: 0.7, d: 0.08 },
    { x: 10.3, y: 0.4, d: 0.07 }, { x: 1.1, y: 1.0, d: 0.05 },
  ].forEach((p) => {
    s.addShape(pptx.shapes.OVAL, {
      x: p.x, y: p.y, w: p.d, h: p.d,
      fill: { color: C.accent, transparency: 35 }, line: { width: 0 },
    });
  });
}

function addPhotoWithGradient(s, photoPath) {
  s.addImage({ path: photoPath, x: 0, y: 0, w: 13.333, h: 7.5, sizing: { type: "cover", w: 13.333, h: 7.5 } });
  const steps = 8; // simulates a gradient via stacked translucent bars — pptxgenjs has no native gradient fill
  for (let i = 0; i < steps; i++) {
    s.addShape(pptx.shapes.RECTANGLE, {
      x: (13.333 / steps) * i, y: 0, w: 13.333 / steps + 0.03, h: 7.5,
      fill: { color: "000000", transparency: 82 - i * 8 }, line: { width: 0 },
    });
  }
}

function shellTitle(pptx, slots) {
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  if (slots.photoPath) addPhotoWithGradient(s, slots.photoPath);
  else addAbstractGlow(s);

  if (slots.variant === "divider") {
    const pillY = 3.35, pillH = 1.05;
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x: SAFE_X, y: pillY, w: 9.5, h: pillH,
      fill: { type: "none" }, line: { color: C.text, width: 2 }, rectRadius: pillH / 2,
    });
    s.addText(slots.label.toUpperCase(), {
      x: SAFE_X + 0.4, y: pillY, w: 8.7, h: pillH,
      fontSize: 30, bold: true, color: C.text, fontFace: FONT, valign: "middle",
    });
    if (slots.subtitle) {
      s.addText(slots.subtitle, {
        x: SAFE_X, y: pillY + pillH + 0.25, w: 9.5, h: 0.6,
        fontSize: 13, bold: true, color: C.text, fontFace: FONT,
      });
    }
  } else {
    if (slots.kicker) {
      s.addText(slots.kicker.toUpperCase(), {
        x: SAFE_X, y: 1.9, w: SAFE_W, h: 0.4,
        fontSize: 13, bold: true, color: C.accent, fontFace: FONT, align: "center", charSpacing: 1,
      });
    }
    s.addText(slots.headline, {
      x: SAFE_X, y: 2.5, w: SAFE_W, h: 1.4,
      fontSize: 36, bold: true, color: C.text, fontFace: FONT, align: "center",
    });
    if (slots.subtitle) {
      s.addText(slots.subtitle, {
        x: SAFE_X + 1.0, y: 4.1, w: SAFE_W - 2, h: 0.9,
        fontSize: 13, color: C.text_muted, fontFace: FONT, align: "center",
      });
    }
  }

  s.addText(slots.footerNote || `${slots.agency}  ·  © ${slots.year || 2026}. All Rights Reserved. Confidential Do Not Distribute.`, {
    x: SAFE_X, y: 7.08, w: 8.2, h: 0.25,
    fontSize: 8, color: "FFFFFF", fontFace: FONT,
  });
  addFooterBranding(s, { client: slots.client });
  return s;
}
```

---

## Shell: `ARCH-HERO-STAT`

**Slots:** `kicker`, `title`, `metrics[4]{value,label,caption}`, `insightLines[]`, `meansLines[]`

```javascript
function shellHeroStat(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, slots);

  const cardW = (SAFE_W - 3 * 0.18) / 4;
  const y = 1.55;
  slots.metrics.slice(0, 4).forEach((m, i) => {
    const x = SAFE_X + i * (cardW + 0.18);
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x, y, w: cardW, h: 2.2,
      fill: { color: C.bg }, line: { color: C.stroke, width: 1.25 }, rectRadius: 0.08,
    });
    s.addText(m.value, {
      x: x + 0.1, y: y + 0.35, w: cardW - 0.2, h: 0.7,
      fontSize: 34, bold: true, color: C.accent, fontFace: FONT, align: "center",
    });
    s.addText(m.label, {
      x: x + 0.12, y: y + 1.15, w: cardW - 0.24, h: 0.45,
      fontSize: 12, color: C.text, fontFace: FONT, align: "center",
    });
    s.addText(m.caption || "", {
      x: x + 0.12, y: y + 1.65, w: cardW - 0.24, h: 0.35,
      fontSize: 10, color: C.text_muted, fontFace: FONT, align: "center",
    });
  });

  addTakeawayStack(s, { insightLines: slots.insightLines, meansLines: slots.meansLines, y: 4.95 });
  return s;
}
```

---

## Shell: `ARCH-COMPARE-SPLIT` (SEO vs GEO)

**Slots:** `kicker`, `title`, `left{heading,bullets[]}`, `right{heading,sub,bullets[]}`, `pivotLabel` (e.g. `"NOW"`)

```javascript
function shellCompareSplit(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, slots);
  const colW = 5.5;
  const y = 1.7;
  const h = 4.5;

  // Left (muted / old world)
  s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: SAFE_X, y, w: colW, h,
    fill: { color: C.bg }, line: { color: C.stroke, width: 1.25 }, rectRadius: 0.1,
  });
  s.addText(slots.left.heading, {
    x: SAFE_X + 0.35, y: y + 0.35, w: colW - 0.7, h: 0.5,
    fontSize: 22, bold: true, color: C.text, fontFace: FONT,
  });
  s.addText(slots.left.bullets.map((b) => `→  ${b}`).join("\n\n"), {
    x: SAFE_X + 0.35, y: y + 1.1, w: colW - 0.7, h: 3.0,
    fontSize: 14, color: C.text, fontFace: FONT,
  });

  s.addText(slots.pivotLabel || "NOW", {
    x: SAFE_X + colW + 0.05, y: y + h / 2 - 0.4, w: 0.9, h: 1.2,
    fontSize: 14, bold: true, color: C.accent, fontFace: FONT, align: "center", rotate: 270,
  });

  // Right (accent / new world)
  const rx = SAFE_X + colW + 1.05;
  s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: rx, y, w: colW, h,
    fill: { color: C.bg }, line: { color: C.stroke, width: 1.25 }, rectRadius: 0.1,
  });
  s.addText(slots.right.heading, {
    x: rx + 0.35, y: y + 0.3, w: colW - 0.7, h: 0.45,
    fontSize: 22, bold: true, color: C.accent, fontFace: FONT,
  });
  if (slots.right.sub) {
    s.addText(slots.right.sub, {
      x: rx + 0.35, y: y + 0.75, w: colW - 0.7, h: 0.4,
      fontSize: 11, color: C.text, fontFace: FONT,
    });
  }
  s.addText(slots.right.bullets.map((b) => `✓  ${b}`).join("\n\n"), {
    x: rx + 0.35, y: y + 1.25, w: colW - 0.7, h: 2.9,
    fontSize: 14, color: C.accent, fontFace: FONT,
  });
  return s;
}
```

---

## Shell: `ARCH-JOURNEY-MAP`

Header fill uses **accent teal** (not orange/coral).

**Slots:** `kicker`, `title`, `rows[{stage,intent,prompts}]` (5 rows)

Still keep `prompts`/`signal` short (≤3 examples, `" · "`-joined) as an authoring habit — but the shell below no longer *relies* on that discipline to stay on-slide. It measures each row from the actual text, shrinks font size if the full table would run past the footer, and passes pptxgenjs a per-row `rowH` array — so even an uncapped or verbose cell degrades gracefully (smaller text) instead of silently overlapping the footer. If a stage has enough genuinely distinct prompts that even the shrunk table feels cramped, move the long tail to `ARCH-JOURNEY-DEEPDIVE` (the 5-card query-taxonomy grid) instead of fighting this table's ceiling.

```javascript
// A content-discipline comment ("cap to 3 examples") is NOT a safety mechanism — nothing enforces
// it, and a 5-row table where two cells wrap to 2 lines (very ordinary real content, e.g. a
// "Signal" or "Example AI Prompts" column carrying data + citation counts) grows past a fixed
// `rowH: 0.85` and runs the table straight into the footer. That happened once already. The fix
// mirrors `estimateIconListHeight`: estimate each row's height from its longest cell's text
// length, sum them, and auto-shrink `fontSize` until the whole table provably fits above
// FOOTER_SAFE_Y — then pass the computed heights to `addTable` as a per-row `rowH` array (which
// pptxgenjs supports) instead of one fixed number for every row.
function shellJourneyMap(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, slots);

  const startY = 1.55;
  const colW = [2.4, 3.6, 6.233];
  const headerH = 0.45;
  const cellOf = (r) => r.prompts ?? r.signal ?? "";

  function layout(fontSize) {
    const charsPerLine = Math.max(20, Math.floor(colW[2] * 12.5 * (11 / fontSize)));
    const lineH = (fontSize / 72) * 1.3;
    const rowH = slots.rows.map((r) => {
      const lines = Math.max(1, Math.ceil(cellOf(r).length / charsPerLine));
      return Math.max(0.55, lines * lineH + 0.32);
    });
    return { rowH, totalH: headerH + rowH.reduce((a, b) => a + b, 0) };
  }

  let fontSize = 11;
  let { rowH, totalH } = layout(fontSize);
  while (startY + totalH > FOOTER_SAFE_Y && fontSize > 8.5) {
    fontSize -= 0.5;
    ({ rowH, totalH } = layout(fontSize));
  }

  const header = [
    { text: "Journey Stage", options: { bold: true, color: C.accent, align: "left" } },
    { text: "Search Intent", options: { bold: true, color: C.accent, align: "left" } },
    { text: slots.rows[0]?.prompts !== undefined ? "Example AI Prompts" : "Signal", options: { bold: true, color: C.accent, align: "left" } },
  ];
  const body = slots.rows.map((r) => [
    { text: r.stage, options: { bold: true, color: C.text, fill: { color: C.bg } } },
    { text: r.intent, options: { color: C.text_muted, fill: { color: C.bg } } },
    { text: cellOf(r), options: { color: C.text, fill: { color: C.bg } } },
  ]);

  s.addTable([header, ...body], {
    x: SAFE_X, y: startY, w: SAFE_W, colW,
    border: { pt: 1, color: C.stroke },
    fontFace: FONT, fontSize, valign: "middle",
    rowH: [headerH, ...rowH],
  });
  return s;
}
```

---

## Shell: `ARCH-GAP-BAR` (highlight client bar)

**Slots:** `kicker`, `title`, `bars[{label,value,isClient,badge}]`, `sidebarHeading`, `sidebarNotes[{icon,text}]`, `meansLines[]`

Client bar = `C.accent`; others = neutral greys from theme (`bar_neutral_*`). Chrome is **left-aligned** (data-dense archetype). The client's own bar — and any bar worth flagging (e.g. "New Entrant") — gets a small boxed badge pill after the value, matching Electrum's "Electrum" / "New Entrant" tags. Sidebar uses `addIconList` (icon-anchored, not plain text cards).

```javascript
function shellGapBar(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, { ...slots, align: "left" });

  const max = Math.max(...slots.bars.map((b) => b.value), 1);
  const chartX = SAFE_X;
  const barMaxW = 4.1; // leaves room for the badge pill before the sidebar starts
  let y = 1.55;
  const neutrals = [C.bar_neutral_1, C.bar_neutral_2, C.bar_neutral_3, C.bar_neutral_4, C.text_dim];

  slots.bars.forEach((b, i) => {
    const w = (b.value / max) * barMaxW;
    const fill = b.isClient ? C.accent : neutrals[i % neutrals.length];
    s.addText(b.label, {
      x: chartX, y, w: 1.9, h: 0.32, fontSize: 11, color: b.isClient ? C.accent : C.text, fontFace: FONT,
      bold: b.isClient,
    });
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x: chartX + 2.0, y: y + 0.02, w: Math.max(w, 0.15), h: 0.28,
      fill: { color: fill }, line: { width: 0 }, rectRadius: 0.04,
    });
    let labelX = chartX + 2.1 + Math.max(w, 0.15);
    s.addText(`${b.value}%`, {
      x: labelX, y, w: 0.7, h: 0.32, fontSize: 11, bold: b.isClient, color: C.text, fontFace: FONT,
    });
    if (b.badge) {
      s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
        x: labelX + 0.65, y: y - 0.01, w: 1.1, h: 0.3,
        fill: { color: C.card_light }, line: { width: 0 }, rectRadius: 0.15,
      });
      s.addText(b.badge, {
        x: labelX + 0.65, y: y - 0.01, w: 1.1, h: 0.3,
        fontSize: 8.5, bold: true, color: C.card_light_text, fontFace: FONT, align: "center", valign: "middle",
      });
    }
    y += 0.48;
  });

  // Sidebar — icon-anchored driver list, not plain text cards. The box height is derived from
  // the notes' own estimated wrap, capped so it can never reach the "What this means" banner at
  // y:5.9 below — this is what silently broke before (fixed h:3.9 assumed ~2-line notes; a
  // 3-line note in a 4-item list overflowed the box and ran into the banner).
  const sx = SAFE_X + 8.3;
  const sw = 3.9;
  const sidebarNotesY = 2.35;
  // Hard ceiling: box must stay clear of the "What this means" banner at y:5.9 (0.15 buffer).
  const notesAvailH = 5.75 - sidebarNotesY;
  const sidebarNoteOpts = { minCardH: 0.5, gap: 0.08, fontSize: 10 };
  let sidebarNotesH = estimateIconListHeight(slots.sidebarNotes, sw - 0.3, sidebarNoteOpts);
  // If 4 notes (or long ones) don't fit even at the floor sizing, shrink font rather than let the
  // box — or worse, the cards themselves — run into the banner below. This is the actual fix:
  // capping the box height alone (a prior attempt) still let the cards overflow past its border.
  while (sidebarNotesH > notesAvailH && sidebarNoteOpts.fontSize > 8) {
    sidebarNoteOpts.fontSize -= 0.5;
    sidebarNotesH = estimateIconListHeight(slots.sidebarNotes, sw - 0.3, sidebarNoteOpts);
  }
  const sidebarH = (sidebarNotesY - 1.55) + Math.min(notesAvailH, sidebarNotesH) + 0.2;
  s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: sx, y: 1.55, w: sw, h: sidebarH,
    fill: { color: C.bg_sidebar }, line: { color: C.stroke_muted, width: 1 }, rectRadius: 0.08,
  });
  s.addText(slots.sidebarHeading || "Why does this happen?", {
    x: sx + 0.2, y: 1.72, w: sw - 0.4, h: 0.55,
    fontSize: 15, bold: true, color: C.text, fontFace: FONT,
  });
  addIconList(s, { x: sx + 0.15, y: sidebarNotesY, w: sw - 0.3, items: slots.sidebarNotes, ...sidebarNoteOpts });

  s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: SAFE_X, y: 5.9, w: 7.8, h: 0.9,
    fill: { color: C.accent_banner }, line: { width: 0 }, rectRadius: 0.06,
  });
  const meansBody = [
    { text: "What this means:\n", options: { bold: true } },
    ...slots.meansLines.flatMap((line, i) => [
      { text: line, options: {} },
      { text: i < slots.meansLines.length - 1 ? "\n" : "", options: {} },
    ]),
  ];
  s.addText(meansBody, {
    x: SAFE_X + 0.25, y: 5.98, w: 7.3, h: 0.74,
    fontSize: 11, color: C.text_on_accent, fontFace: FONT, valign: "middle",
  });
  return s;
}
```

---

## Shell: `ARCH-SOURCE-MATRIX`

**Slots:** `kicker`, `title`, `rows[{domain,role,citations,lever}]`, `insightLines[]`, `meansLines[]`  
Chrome **left-aligned** (matrix). Composition: full-width 4-col table + takeaway stack (not another card grid).

```javascript
function shellSourceMatrix(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, { ...slots, align: "left" });
  const header = [
    { text: "Domain / Source", options: { bold: true, color: C.accent } },
    { text: "Category Role", options: { bold: true, color: C.accent } },
    { text: "Citations", options: { bold: true, color: C.accent } },
    { text: "Client Action Lever", options: { bold: true, color: C.accent } },
  ];
  const body = slots.rows.map((r) => [
    { text: r.domain, options: { bold: true, color: C.text, fill: { color: C.bg } } },
    { text: r.role, options: { color: C.text_muted, fill: { color: C.bg } } },
    { text: String(r.citations), options: { color: C.accent, bold: true, fill: { color: C.bg } } },
    { text: r.lever, options: { color: C.text, fill: { color: C.bg } } },
  ]);
  s.addTable([header, ...body], {
    x: SAFE_X, y: 1.55, w: SAFE_W, colW: [3.0, 2.2, 1.5, 5.533],
    border: { pt: 1, color: C.stroke },
    fontFace: FONT, fontSize: 10.5, valign: "middle", rowH: 0.56,
  });
  addTakeawayStack(s, {
    insightLines: slots.insightLines,
    meansLines: slots.meansLines,
    y: 5.85,
  });
  return s;
}
```

---

## Shell: `ARCH-TECH-AUDIT`

**Slots:** `kicker`, `title`, `cards[6]{label,score,status,warn?}`, `insightLines[]`, `meansLines[]`  
Chrome **center**. Composition: **2×3 scorecard** (different from HERO 1×4 and VOICE 2×2). `warn: true` → score uses `C.semantic_warn`.

```javascript
function shellTechAudit(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, slots);
  const cols = 3, gap = 0.18;
  const cardW = (SAFE_W - (cols - 1) * gap) / cols;
  const cardH = 1.55;
  const startY = 1.55;
  slots.cards.slice(0, 6).forEach((c, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = SAFE_X + col * (cardW + gap);
    const y = startY + row * (cardH + gap);
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x, y, w: cardW, h: cardH,
      fill: { color: C.bg }, line: { color: C.stroke, width: 1.25 }, rectRadius: 0.08,
    });
    s.addText(c.label, {
      x: x + 0.15, y: y + 0.12, w: cardW - 0.3, h: 0.32,
      fontSize: 10.5, bold: true, color: C.text_muted, fontFace: FONT,
    });
    s.addText(c.score, {
      x: x + 0.15, y: y + 0.42, w: cardW - 0.3, h: 0.5,
      fontSize: 20, bold: true, color: c.warn ? C.semantic_warn : C.accent, fontFace: FONT,
    });
    s.addText(c.status, {
      x: x + 0.15, y: y + 0.98, w: cardW - 0.3, h: 0.5,
      fontSize: 9.5, color: C.text, fontFace: FONT,
    });
  });
  addTakeawayStack(s, {
    insightLines: slots.insightLines,
    meansLines: slots.meansLines,
    y: 5.15,
  });
  return s;
}
```

---

## Shell: `ARCH-VOICE-GRID`

**Slots:** `kicker`, `title`, `quotes[4]{text,source}`, `insightLines[]`, `meansLines[]`  
Chrome **center**. Composition: **2×2 quote cards** on `bg_card` (not equal metric boxes). Italic quote + accent source line.

```javascript
function shellVoiceGrid(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, slots);
  const cols = 2, gap = 0.2;
  const cardW = (SAFE_W - gap) / cols;
  const cardH = 1.55;
  const startY = 1.6;
  slots.quotes.slice(0, 4).forEach((q, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = SAFE_X + col * (cardW + gap);
    const y = startY + row * (cardH + gap);
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x, y, w: cardW, h: cardH,
      fill: { color: C.bg_card }, line: { color: C.stroke_muted, width: 1 }, rectRadius: 0.08,
    });
    s.addText(`"${q.text}"`, {
      x: x + 0.25, y: y + 0.15, w: cardW - 0.5, h: cardH - 0.55,
      fontSize: 11.5, italic: true, color: C.text, fontFace: FONT,
    });
    s.addText(`— ${q.source}`, {
      x: x + 0.25, y: y + cardH - 0.38, w: cardW - 0.5, h: 0.3,
      fontSize: 9.5, color: C.accent, fontFace: FONT,
    });
  });
  addTakeawayStack(s, {
    insightLines: slots.insightLines,
    meansLines: slots.meansLines,
    y: 5.05,
  });
  return s;
}
```

---

## Shell: `ARCH-RECOMMENDATION-SPLIT`

**Slots:** `kicker`, `title`, `pillars[3]{heading,bullets[]}`, `insightLines[]`, `meansLines[]`  
Chrome **center**. Composition: **3 vertical pillars** with accent header bar (not a flat N-box metric row).

```javascript
function shellRecommendationSplit(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, slots);
  const colW = (SAFE_W - 2 * 0.2) / 3;
  const y = 1.6;
  const h = 3.9;
  slots.pillars.slice(0, 3).forEach((p, i) => {
    const x = SAFE_X + i * (colW + 0.2);
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x, y, w: colW, h,
      fill: { color: C.bg }, line: { color: C.stroke, width: 1.25 }, rectRadius: 0.1,
    });
    s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
      x, y, w: colW, h: 0.55,
      fill: { color: C.accent_deep }, line: { width: 0 }, rectRadius: 0.1,
    });
    s.addText(p.heading, {
      x: x + 0.2, y: y + 0.08, w: colW - 0.4, h: 0.4,
      fontSize: 13, bold: true, color: C.text_on_accent, fontFace: FONT,
    });
    s.addText(p.bullets.map((b) => `•  ${b}`).join("\n\n"), {
      x: x + 0.25, y: y + 0.75, w: colW - 0.5, h: h - 1.0,
      fontSize: 11, color: C.text, fontFace: FONT,
    });
  });
  addTakeawayStack(s, {
    insightLines: slots.insightLines,
    meansLines: slots.meansLines,
    y: 5.65,
  });
  return s;
}
```

---

## Shell: `ARCH-PRIORITY-ACTION`

**Slots:** `kicker`, `title`, `sprint[]` (30-day checklist), `phases[{name,desc}]` (up to 4)  
Chrome **center**. Composition: **60/40 split** — checklist left, phased roadmap right (asymmetric vs recommendation pillars).

**Per-phase spacing is computed from `phases.length`, never hardcoded.** A fixed `py += 1.1` step (sized for 3 phases) silently pushes a 4th phase's description past the box's bottom border — that exact bug shipped once already. Both columns share one `h` computed from whichever slot (sprint or phases) needs more room, capped so the box never approaches the footer.

```javascript
function shellPriorityAction(pptx, slots) {
  const s = pptx.addSlide();
  addChrome(s, slots);
  const colW = 5.6;
  const y = 1.6;
  const maxH = FOOTER_SAFE_Y - y; // never let either column reach the footer, regardless of item count
  const h = Math.min(5.1, maxH);

  s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: SAFE_X, y, w: colW, h,
    fill: { color: C.bg }, line: { color: C.stroke, width: 1.25 }, rectRadius: 0.1,
  });
  s.addText("30-DAY QUICK WINS SPRINT", {
    x: SAFE_X + 0.3, y: y + 0.25, w: colW - 0.6, h: 0.4,
    fontSize: 15, bold: true, color: C.accent, fontFace: FONT,
  });
  s.addText(slots.sprint.map((item) => `☐  ${item}`).join("\n\n"), {
    x: SAFE_X + 0.3, y: y + 0.85, w: colW - 0.6, h: h - 1.1,
    fontSize: 11.5, color: C.text, fontFace: FONT,
  });

  const rx = SAFE_X + colW + 0.4;
  const rw = SAFE_W - colW - 0.4;
  s.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: rx, y, w: rw, h,
    fill: { color: C.bg_sidebar }, line: { color: C.stroke_muted, width: 1 }, rectRadius: 0.1,
  });
  s.addText("6-MONTH PHASED ROADMAP", {
    x: rx + 0.3, y: y + 0.25, w: rw - 0.6, h: 0.4,
    fontSize: 15, bold: true, color: C.accent, fontFace: FONT,
  });
  const phases = slots.phases.slice(0, 4);
  const phaseTop = y + 0.95;
  const phaseAvailH = h - 0.95 - 0.15; // leave a bottom margin inside the box
  const phaseStep = Math.min(1.1, phaseAvailH / phases.length);
  const nameH = 0.3;
  const descH = Math.max(0.4, phaseStep - nameH - 0.08);
  phases.forEach((ph, i) => {
    const py = phaseTop + i * phaseStep;
    s.addText(ph.name, {
      x: rx + 0.3, y: py, w: rw - 0.6, h: nameH,
      fontSize: 12, bold: true, color: C.text, fontFace: FONT,
    });
    s.addText(ph.desc, {
      x: rx + 0.3, y: py + nameH + 0.02, w: rw - 0.6, h: descH,
      fontSize: phases.length > 3 ? 9.5 : 10.5, color: C.text_muted, fontFace: FONT,
    });
  });
  return s;
}
```

---

## Production checklist

1. Load `design-theme.json` (or client override of `accent` only).
2. Map narrative → archetype IDs from `slide-archetypes.md`.
3. Call the matching `shell*` with slot JSON — **do not** hand-draw coordinates.
4. Pick chrome alignment per `chrome.title_align_variants` (left for chart/table/matrix archetypes, center for card-grid/quote archetypes) and pass `title` as `"Lead text|Emphasis punchline"` so `addChrome` renders the two-tone headline.
5. Use `shellTitle` for cover + section breaks + closing CTA — pass `photoPath` if a client photo asset exists (same image reused across all three, never per-slide AI art); otherwise it renders the abstract-glow fallback automatically. Never leave a title/closing slide flat black, and never put the client name in the cover kicker — use a category tag instead.
6. Use `addIconList` for any "why/what/how" driver sidebar instead of plain text cards — pass a plain icon glyph in `item.icon` (one per line, from `theme.icons`), matching Electrum's own usage.
7. Vary card composition per archetype — never repeat the same equal-width N-box grid shape on consecutive slides.
8. Pass `insightLines` as slots (never hardcode client-specific copy inside shell functions).
9. Run anti-slop QA (`anti-slop-rules.md`).
10. Write `[Brand]_GEO_Audit_YYYY.pptx`.

```javascript
await pptx.writeFile({ fileName: `${brand}_GEO_Audit_2026.pptx` });
```
