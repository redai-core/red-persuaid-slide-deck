# Slide Deck Code & Generation Templates

When the user requests executable code or exportable slide decks for their presentation, use one of these standard implementation approaches based on their preferred stack:

---

## 1. Single-File High-Fidelity HTML / CSS Presentation (Recommended)

Single-file HTML with embedded Tailwind CSS and Alpine.js / vanilla JS keyboard navigation (`ArrowRight`, `ArrowLeft`, `Space`). This preserves 100% executive typography, modern rounded cards, accent badges, and clean contrast.

### HTML Boilerplate Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Deck Title] — [Client Name]</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #0B0F17;
      color: #F3F4F6;
    }
    .slide {
      display: none;
      width: 100vw;
      height: 100vh;
      aspect-ratio: 16/9;
    }
    .slide.active {
      display: flex;
    }
  </style>
</head>
<body class="flex items-center justify-center min-h-screen select-none">
  <div id="deck-container" class="relative w-full h-full max-w-[1920px] max-h-[1080px] bg-[#0d131f] border border-gray-800 shadow-2xl overflow-hidden flex flex-col justify-between p-12">
    
    <!-- Slide 1: Cover -->
    <div class="slide active flex flex-col justify-between h-full">
      <div class="flex items-center justify-between">
        <span class="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold tracking-widest uppercase rounded">Strategic Analysis</span>
        <span class="text-xs font-semibold text-gray-400">[Date / Prepared By]</span>
      </div>
      <div class="my-auto space-y-4">
        <h1 class="text-6xl font-extrabold tracking-tight text-white">[Deck Main Title]</h1>
        <p class="text-2xl text-gray-300 font-light">[Subtitle / Core Strategic Question]</p>
      </div>
      <div class="flex items-center justify-between border-t border-gray-800 pt-6 text-sm text-gray-400">
        <div>Market: [Target Geography]</div>
        <div class="flex space-x-6">
          <span>[Metric A]</span>
          <span>·</span>
          <span>[Metric B]</span>
          <span>·</span>
          <span>[Metric C]</span>
        </div>
      </div>
    </div>

    <!-- Additional slides follow the Archetype Catalog -->

    <!-- Navigation Overlay -->
    <div class="absolute bottom-4 right-6 flex items-center space-x-2 text-xs text-gray-500">
      <span id="slide-num">Slide 1 / 14</span>
      <span class="text-gray-600">· Use ← → keys</span>
    </div>
  </div>

  <script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const slideNum = document.getElementById('slide-num');

    function showSlide(index) {
      slides[currentSlide].classList.remove('active');
      currentSlide = (index + slides.length) % slides.length;
      slides[currentSlide].classList.add('active');
      if (slideNum) slideNum.innerText = `Slide ${currentSlide + 1} / ${slides.length}`;
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') showSlide(currentSlide + 1);
      if (e.key === 'ArrowLeft') showSlide(currentSlide - 1);
    });
  </script>
</body>
</html>
```

---

## 2. Native PowerPoint via Python-PPTX

When generating binary `.pptx` presentations programmatically:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

DARK_BG = RGBColor(13, 19, 31)
ACCENT_GREEN = RGBColor(16, 185, 129)
TEXT_WHITE = RGBColor(255, 255, 255)

def create_stat_slide(prs, kicker, title, stats, synthesis):
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_BG
    bg.line.fill.background()
    
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(1.2))
    tf = txBox.text_frame
    p_kicker = tf.paragraphs[0]
    p_kicker.text = kicker.upper()
    p_kicker.font.size = Pt(11)
    p_kicker.font.bold = True
    p_kicker.font.color.rgb = ACCENT_GREEN
    
    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE
    
    return slide
```

---

## 3. Marp Markdown Export Template

When using Marp CLI (`marp presentation.md --pptx` or `--html`):

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    background-color: #0d131f;
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

> **What this means:** The gap is frequency, not reputation. Editorial distribution is the primary lever.
```
