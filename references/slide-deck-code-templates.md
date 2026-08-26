# Slide Deck Code & Generation Templates

PersuAId generates native **16:9 HD widescreen (`13.333" × 7.5"`) PowerPoint presentation decks** directly using `pptxgenjs`.

---

## Standard Node.js PptxGenJS Generator (`generate_deck.js`)

When generating presentations directly in the workspace, create and run a Node.js script using `pptxgenjs` with the standard 16:9 HD widescreen layout:

```javascript
import pptxgen from "pptxgenjs";

const pptx = new pptxgen();

// Define Standard Modern 16:9 Widescreen Layout (13.333" x 7.5" / 1920x1080 equivalent)
pptx.defineLayout({ name: "LAYOUT_16_9_HD", width: 13.333, height: 7.5 });
pptx.layout = "LAYOUT_16_9_HD";

pptx.author = "PersuAId Strategy & GEO Intelligence";
pptx.company = "PersuAId";
pptx.title = "[Brand] - Generative Engine Optimization (GEO) & AI Category Audit";

// Color Palette Constants (Dark Executive Theme)
const BG_DARK = "07090E";
const BG_CARD = "0E131F";
const BG_CARD_LIGHT = "151C2E";
const TEXT_WHITE = "FFFFFF";
const TEXT_MUTED = "94A3B8";
const TEXT_DIM = "64748B";
const ACCENT_EMERALD = "10B981";
const ACCENT_BLUE = "3B82F6";
const ACCENT_RED = "EF4444";
const ACCENT_AMBER = "F59E0B";

// Geometry Margins (16:9 HD 13.333" x 7.5")
const SAFE_X = 0.8;
const SAFE_W = 11.733;

// Helper: Standard Slide Header
function addHeader(slide, kicker, title, subtitle = null) {
  slide.background = { color: BG_DARK };

  slide.addText(kicker.toUpperCase(), {
    x: SAFE_X,
    y: 0.45,
    w: SAFE_W,
    h: 0.25,
    fontSize: 9.5,
    bold: true,
    color: ACCENT_EMERALD,
    fontFace: "Arial",
  });

  slide.addText(title, {
    x: SAFE_X,
    y: 0.72,
    w: SAFE_W,
    h: 0.65,
    fontSize: 19,
    bold: true,
    color: TEXT_WHITE,
    fontFace: "Arial",
  });

  if (subtitle) {
    slide.addText(subtitle, {
      x: SAFE_X,
      y: 1.38,
      w: SAFE_W,
      h: 0.35,
      fontSize: 11,
      color: TEXT_MUTED,
      fontFace: "Arial",
    });
  }

  // Footer
  slide.addText("PersuAId Strategy & GEO Intelligence · Confidential", {
    x: SAFE_X,
    y: 6.85,
    w: SAFE_W,
    h: 0.25,
    fontSize: 9,
    color: TEXT_DIM,
    fontFace: "Arial",
  });
}

// Helper: Synthesis / Takeaway Box
function addSynthesis(slide, text, yPos = 5.75, h = 0.85) {
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: SAFE_X,
    y: yPos,
    w: SAFE_W,
    h: h,
    fill: { color: BG_CARD },
    line: { color: ACCENT_EMERALD, width: 1.5 },
  });

  slide.addText("WHAT THIS MEANS:", {
    x: SAFE_X + 0.2,
    y: yPos + 0.08,
    w: SAFE_W - 0.4,
    h: 0.2,
    fontSize: 8.5,
    bold: true,
    color: ACCENT_EMERALD,
    fontFace: "Arial",
  });

  slide.addText(text, {
    x: SAFE_X + 0.2,
    y: yPos + 0.28,
    w: SAFE_W - 0.4,
    h: h - 0.35,
    fontSize: 10,
    color: TEXT_WHITE,
    fontFace: "Arial",
  });
}

// -------------------------------------------------------------
// SLIDE 1: Cover (ARCH-TITLE)
// -------------------------------------------------------------
const slide1 = pptx.addSlide();
slide1.background = { color: BG_DARK };

slide1.addText("GENERATIVE ENGINE OPTIMIZATION (GEO) AUDIT", {
  x: SAFE_X,
  y: 2.2,
  w: SAFE_W,
  fontSize: 11,
  bold: true,
  color: ACCENT_EMERALD,
  fontFace: "Arial",
});

slide1.addText("[Brand Name]", {
  x: SAFE_X,
  y: 2.55,
  w: SAFE_W,
  fontSize: 40,
  bold: true,
  color: TEXT_WHITE,
  fontFace: "Arial",
});

slide1.addText("AI Search Visibility, Category Mindshare & Strategic Remediation Blueprint", {
  x: SAFE_X,
  y: 3.5,
  w: SAFE_W,
  fontSize: 16,
  color: ACCENT_BLUE,
  fontFace: "Arial",
});

// -------------------------------------------------------------
// SLIDE 3: Search Journey Overview Table (ARCH-JOURNEY-MAP)
// -------------------------------------------------------------
const slide3 = pptx.addSlide();
addHeader(slide3, "SEARCH JOURNEY", "Who we're reaching, and the journey we must own end-to-end");

const journeyTableData = [
  [
    { text: "JOURNEY STAGE", options: { bold: true, color: "FFFFFF", fill: { color: "FA541C" }, fontSize: 10 } },
    { text: "SEARCH INTENT", options: { bold: true, color: "FFFFFF", fill: { color: "FA541C" }, fontSize: 10 } },
    { text: "REPRESENTATIVE USER QUERIES / TOPICS", options: { bold: true, color: "FFFFFF", fill: { color: "FA541C" }, fontSize: 10 } },
  ],
  [
    { text: "1. Discovery", options: { bold: true, color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9.5 } },
    { text: "Unbranded category, inspiration, problem-solving", options: { color: "94A3B8", fill: { color: "0E131F" }, fontSize: 9 } },
    { text: '"Warna cat ruang tamu yang sejuk" · "merk cat tembok interior terbaik 2026" · "inspirasi warna cat kamar sempit"', options: { color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9 } },
  ],
  [
    { text: "2. Interest", options: { bold: true, color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9.5 } },
    { text: "Brand-specific, product lines, features & colors", options: { color: "94A3B8", fill: { color: "0E131F" }, fontSize: 9 } },
    { text: '"Jotun Majestic True Beauty" · "katalog warna cat Jotun 2026" · "harga cat Jotun interior 5kg"', options: { color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9 } },
  ],
  [
    { text: "3. Consideration", options: { bold: true, color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9.5 } },
    { text: "Brand/product comparison & reviews", options: { color: "94A3B8", fill: { color: "0E131F" }, fontSize: 9 } },
    { text: '"Jotun vs Dulux interior" · "Jotun Majestic vs Essence" · "review Jotun Majestic Sense" · "apakah cat Jotun bagus?"', options: { color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9 } },
  ],
  [
    { text: "4. Purchase", options: { bold: true, color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9.5 } },
    { text: "Purchase intent, local availability, pricing", options: { color: "94A3B8", fill: { color: "0E131F" }, fontSize: 9 } },
    { text: '"Toko cat Jotun terdekat" · "harga cat Jotun 25 kg warna putih" · "Jotun official store Tokopedia"', options: { color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9 } },
  ],
  [
    { text: "5. After purchase", options: { bold: true, color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9.5 } },
    { text: "Application, maintenance, support & advocacy", options: { color: "94A3B8", fill: { color: "0E131F" }, fontSize: 9 } },
    { text: '"Cara mengaplikasikan Jotun Majestic" · "cara membersihkan noda di dinding Jotun" · "sisa cat Jotun tahan berapa lama"', options: { color: "FFFFFF", fill: { color: "0E131F" }, fontSize: 9 } },
  ],
];

slide3.addTable(journeyTableData, {
  x: SAFE_X,
  y: 1.6,
  w: SAFE_W,
  colW: [2.0, 3.8, 5.933],
  border: { pt: 0.5, color: "334155" },
  align: "left",
  valign: "middle",
});

// -------------------------------------------------------------
// SLIDE 4: Complete Prompt Taxonomy Grid (ARCH-JOURNEY-DEEPDIVE)
// -------------------------------------------------------------
const slide4 = pptx.addSlide();
addHeader(slide4, "QUERY TAXONOMY", "Prompt mapped to journey", "Jotun Cat Interior");

// Helper: 5-Stage Container Card (Dark Header Bar + Crisp White Card Body)
function addJourneyCard(slide, title, bullets, x, y, w, h) {
  // Dark Header Bar
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: x,
    y: y,
    w: w,
    h: 0.35,
    fill: { color: "111827" },
    line: { color: "374151", width: 1 },
  });

  slide.addText(title.toUpperCase(), {
    x: x + 0.15,
    y: y + 0.05,
    w: w - 0.3,
    h: 0.25,
    fontSize: 9.5,
    bold: true,
    color: "FFFFFF",
    fontFace: "Arial",
  });

  // White Card Body
  slide.addShape(pptx.shapes.RECTANGLE, {
    x: x,
    y: y + 0.35,
    w: w,
    h: h - 0.35,
    fill: { color: "FFFFFF" },
    line: { color: "E5E7EB", width: 1 },
  });

  const bulletText = bullets.map(b => `• ${b}`).join("\n");
  slide.addText(bulletText, {
    x: x + 0.15,
    y: y + 0.45,
    w: w - 0.3,
    h: h - 0.55,
    fontSize: 8.2,
    color: "111827",
    fontFace: "Arial",
    lineSpacing: 12,
  });
}

// Row 1 (Top - 3 Cards)
addJourneyCard(slide4, "1 · DISCOVERY", [
  "cat interior terbaik",
  "warna cat ruang tamu 2026",
  "warna kamar agar terlihat luas",
  "cat tembok anti lembab",
  "cat interior low odor",
  "cat tembok interior anti jamur",
  "inspirasi warna kamar sempit",
  "warna cat rumah minimalis"
], 0.8, 1.65, 3.75, 2.35);

addJourneyCard(slide4, "2 · INTEREST", [
  "Jotun cat interior",
  "warna cat interior Jotun",
  "katalog warna cat Jotun 2026",
  "Jotun Majestic Wall",
  "Jotun Majestic True Beauty",
  "Jotun untuk kamar tidur",
  "cat low odour kamar anak",
  "rekomendasi Jotun ruang keluarga"
], 4.79, 1.65, 3.75, 2.35);

addJourneyCard(slide4, "3 · CONSIDERATION", [
  "Jotun vs Dulux interior",
  "Jotun Majestic Sense vs True Beauty",
  "Jotun Majestic vs Essence",
  "review Jotun Majestic Sense",
  "apakah cat Jotun bagus?",
  "cat matt vs sheen",
  "cat Jotun terbaik kamar anak",
  "Jotun vs Nippon Paint interior"
], 8.78, 1.65, 3.75, 2.35);

// Row 2 (Bottom - 2 Cards)
addJourneyCard(slide4, "4 · PURCHASE", [
  "harga cat Jotun interior",
  "toko cat Jotun terdekat",
  "Jotun official store",
  "Jotun official store Tokopedia",
  "promo cat Jotun terbaru",
  "beli sampel warna Jotun",
  "kalkulator kebutuhan cat Jotun",
  "agen resmi Jotun Jakarta"
], 0.8, 4.25, 5.74, 2.35);

addJourneyCard(slide4, "5 · AFTER PURCHASE", [
  "cara menggunakan cat Jotun",
  "cara mengaplikasikan Jotun Majestic",
  "apakah perlu primer sebelum mengecat?",
  "berapa lapis cat Jotun?",
  "berapa lama cat interior kering?",
  "cara membersihkan noda di dinding",
  "hasil warna Jotun setelah kering",
  "review setelah pakai Jotun Majestic"
], 6.79, 4.25, 5.74, 2.35);

pptx.writeFile({ fileName: "[Brand]_GEO_Audit_2026.pptx" });
```
