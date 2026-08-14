# Slide Deck Code & Generation Templates

PersuAId prioritizes a **zero-friction, zero-install user experience**. By embedding client-side PowerPoint generation (`pptxgenjs`) and print CSS directly into the single-file HTML deliverable, non-technical users can view slides, present in fullscreen, and download native editable `.pptx` or `.pdf` files **with a single click and zero CLI dependencies**.

---

## 1. Zero-Install Interactive HTML + Instant In-Browser PPTX Exporter (Standard Deliverable)

This single-file HTML deck contains:
- **Presentation Mode**: Fullscreen, keyboard shortcuts (`←`, `→`, `Space`, `F`), swipe on mobile.
- **1-Click PPTX Export**: In-browser client-side generator that converts slides into native `.pptx` on click.
- **1-Click PDF Export**: Clean `@media print` styling for browser "Print to PDF".
- **Zero Dependencies**: Requires no Node.js, Python, or terminal commands.

### Complete Standalone Boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Deck Title] — [Client Name]</title>
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Client-side PPTX Generator (Zero install for user) -->
  <script src="https://cdn.jsdelivr.net/npm/pptxgenjs@3.12.0/dist/pptxgen.bundle.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  
  <style>
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #07090E;
      color: #F3F4F6;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }
    .slide-viewport {
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .slide-frame {
      width: 100%;
      height: 100%;
      max-width: 1600px;
      max-height: 900px;
      aspect-ratio: 16 / 9;
      background-color: #0B0F17;
      position: relative;
      overflow: hidden;
      display: none;
      flex-direction: column;
      justify-content: space-between;
      padding: 3.5rem 4.5rem;
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }
    .slide-frame.active {
      display: flex;
      animation: fadeIn 0.2s ease-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: scale(0.995); }
      to { opacity: 1; transform: scale(1); }
    }
    .kicker {
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: #10B981;
    }
    .synthesis-box {
      background: rgba(255, 255, 255, 0.03);
      border-left: 3px solid #10B981;
      border-radius: 0.375rem;
      padding: 0.85rem 1.25rem;
    }
    .metric-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 0.5rem;
      padding: 1.25rem;
    }

    /* Print to PDF Styles */
    @media print {
      body { overflow: visible; background: transparent; }
      .slide-viewport { display: block; width: 100%; height: auto; }
      .slide-frame {
        display: flex !important;
        page-break-after: always;
        break-after: page;
        width: 100vw;
        height: 56.25vw;
        max-width: none;
        max-height: none;
        border: none;
        box-shadow: none;
      }
      .no-print { display: none !important; }
    }
  </style>
</head>
<body class="select-none">

  <div class="slide-viewport">
    
    <!-- SLIDE 1 -->
    <section class="slide-frame active" data-kicker="EXECUTIVE REPORT" data-title="Strategic Analysis" data-subtitle="Market Category Assessment">
      <div class="flex items-center justify-between">
        <span class="kicker">STRATEGIC REPORT</span>
        <span class="text-xs text-gray-500 font-medium">Prepared by Captain Words</span>
      </div>
      <div class="my-auto py-8 space-y-4">
        <h1 class="text-5xl lg:text-6xl font-black tracking-tight text-white">[Brand Name]</h1>
        <p class="text-xl text-gray-300 font-light max-w-3xl">[Core Strategic Subtitle]</p>
      </div>
      <div class="flex items-center justify-between border-t border-gray-800/80 pt-4 text-xs text-gray-500">
        <div>Market: Indonesia</div>
        <div class="font-mono text-gray-400">1 / 5</div>
      </div>
    </section>

    <!-- Additional slides follow Archetype Catalog -->

  </div>

  <!-- Zero-Friction Controller & Export Toolbar (Hidden in Print) -->
  <div class="no-print fixed bottom-4 right-6 flex items-center space-x-3 bg-gray-900/90 border border-gray-800 px-4 py-2 rounded-full text-xs text-gray-400 backdrop-blur shadow-2xl z-50">
    <button onclick="prevSlide()" class="hover:text-white px-2 py-0.5">← Prev</button>
    <span id="slide-indicator" class="font-mono text-white text-[11px]">1 / 5</span>
    <button onclick="nextSlide()" class="hover:text-white px-2 py-0.5">Next →</button>
    <span class="text-gray-700">|</span>
    <button onclick="downloadPptx()" class="hover:text-emerald-400 text-emerald-300 font-semibold flex items-center space-x-1">
      <span>📥 Export .PPTX</span>
    </button>
    <span class="text-gray-700">|</span>
    <button onclick="window.print()" class="hover:text-white">🖨️ PDF</button>
    <span class="text-gray-700">|</span>
    <button onclick="toggleFullscreen()" class="hover:text-white">⛶ Fullscreen</button>
  </div>

  <script>
    let currentIdx = 0;
    const slides = document.querySelectorAll('.slide-frame');
    const indicator = document.getElementById('slide-indicator');

    function showSlide(idx) {
      slides[currentIdx].classList.remove('active');
      currentIdx = (idx + slides.length) % slides.length;
      slides[currentIdx].classList.add('active');
      if (indicator) indicator.innerText = `${currentIdx + 1} / ${slides.length}`;
    }

    function nextSlide() { showSlide(currentIdx + 1); }
    function prevSlide() { showSlide(currentIdx - 1); }

    function toggleFullscreen() {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen();
      else if (document.exitFullscreen) document.exitFullscreen();
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); nextSlide(); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prevSlide(); }
      else if (e.key === 'f' || e.key === 'F') toggleFullscreen();
      else if (e.key === 'Home') showSlide(0);
      else if (e.key === 'End') showSlide(slides.length - 1);
    });

    // Zero-Install Client-Side PowerPoint Exporter
    function downloadPptx() {
      if (typeof PptxGenJS === 'undefined') {
        alert('PowerPoint generator loading, please try again in a second.');
        return;
      }
      let pptx = new PptxGenJS();
      pptx.layout = 'LAYOUT_16x9';

      slides.forEach((s, idx) => {
        let slide = pptx.addSlide();
        slide.background = { color: '0B0F17' };

        let kicker = s.getAttribute('data-kicker') || 'EXECUTIVE PRESENTATION';
        let title = s.getAttribute('data-title') || s.querySelector('h1, h2')?.innerText || 'Slide';
        let subtitle = s.getAttribute('data-subtitle') || '';

        // Add Header
        slide.addText(kicker.toUpperCase(), { x: 0.8, y: 0.6, fontSize: 11, bold: true, color: '10B981', fontFace: 'Arial' });
        slide.addText(title, { x: 0.8, y: 0.9, w: 11.7, fontSize: 22, bold: true, color: 'FFFFFF', fontFace: 'Arial' });
        if (subtitle) {
          slide.addText(subtitle, { x: 0.8, y: 1.5, w: 11.7, fontSize: 13, color: '9CA3AF', fontFace: 'Arial' });
        }

        // Add Footer
        slide.addText(`PersuAId Executive Report · Slide ${idx + 1}`, { x: 0.8, y: 6.8, w: 11.7, fontSize: 9, color: '6B7280', fontFace: 'Arial' });
      });

      pptx.writeFile({ fileName: 'presentation.pptx' });
    }
  </script>
</body>
</html>
```

---

## 2. Optional: Marp CLI Markdown Template (For Markdown Enthusiasts)

For users who already have `npx` / Marp installed:

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    background-color: #0b0f17;
    color: #f3f4f6;
    font-family: 'Plus Jakarta Sans', sans-serif;
    padding: 40px;
  }
  h1 { color: #ffffff; font-size: 28px; }
  .kicker { color: #10b981; font-weight: bold; font-size: 14px; text-transform: uppercase; }
  .box { background: #172033; border: 1px solid #2d3748; border-radius: 8px; padding: 16px; }
---

<!-- Slide 1 -->
<div class="kicker">Core Finding</div>

# Visible but underpowered — the AI gap is real

<div class="box">

**9.3%** AI Mention Share | **#4** Category Rank | **63/100** Sentiment Score

</div>

> **What this means:** The gap is frequency, not reputation. Distribution is the primary lever.
```

Conversion one-liner:
```bash
npx @marp-team/marp-cli presentation.md --pptx
```
