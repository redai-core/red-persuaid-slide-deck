# Strategic Discovery & GEO Engineering Framework (Step 1)

This framework governs how PersuAId extracts strategic context from the client and translates it into an AI visibility audit and executive presentation.

---

## Core Philosophy: Division of Responsibility

| Role | Entity | Responsibilities |
| :--- | :--- | :--- |
| **Business Reality** | **The Client** | Provides brand name, target geography, buyer personas, product USPs, competitors, and pain points. (Things only the client knows). |
| **Search Engine Intelligence** | **PersuAId Engine** | **Automatically reverse-engineers** the multi-platform **5-Stage AI Search Journey** (*Discovery*, *Interest*, *Consideration*, *Purchase*, *After-Purchase*) across ChatGPT, Google AI Overviews, Gemini, and Perplexity. |

> ⚠️ **Rule**: The client is **never** asked to formulate or brainstorm search queries. That is the core function of PersuAId's GEO intelligence engine.

---

## Part 1: The Client Interview (Questions for the Client)

When starting a new presentation or audit without a pre-existing brief, ask the user these focused strategic discovery questions:

### 1. Brand & Web Domain
* What is the exact brand name, website domain URL, and parent company backing?
* What is the brand's standing (category leader, legacy incumbent, challenger, or new entrant)?

### 2. Location & Geographic Scope
* What is the primary target country and geographic focus (e.g. major metropolitan areas, high-growth regional corridors)?
* Are there specific regional or climate nuances (e.g. tropical humidity, urban traffic, local infrastructure)?

### 3. Language & Category Lexicon
* What is the primary operating language?
* What common industry loanwords or technical terms do customers use (e.g. *"battery swap"*, *"range anxiety"*, *"TCO"*, *"low odor"*, *"matte finish"*)?

### 4. Target Audience & Buyer Persona
* Who is your ideal customer (B2C consumers, young families, daily commuters, fleet managers, trade professionals)?
* What is their key decision-making trigger?

### 5. Product USPs & The Moat
* What is your core product offering and flagship line?
* What makes your product unique, superior, or distinct from alternatives (the unfair advantage or moat)?

### 6. Competitor Landscape
* Who are the top 3–5 market competitors or alternative solutions you want benchmarked?
* How are competitors currently perceived in the market?

### 7. Customer Pain Points & Objections
* What specific frictions, anxieties, or hesitations prevent customers from buying or adopting your product?

---

## Part 2: The AI Reverse-Prompting Engine (PersuAId's Role)

Once the client provides their business context from Part 1, **PersuAId does NOT guess or hand-craft prompts**. Instead, it **reverse-prompts major AI platforms (ChatGPT, Gemini)** to extract the authentic, high-volume search queries that real users actually ask across the 5 buyer journey stages in the target market:

```
[ Client Business Context ] ──► [ Reverse-Prompting Engine ] ──► [ Authentic Multi-Platform User Prompts ]
```

### The 5-Stage AI Search Journey Taxonomy:

| Journey Stage | Strategic Objective | AI Reverse-Prompting Perspective | Target Platforms |
| :--- | :--- | :--- | :--- |
| **1. Discovery** | Test unprompted organic category recommendations & pain-point solutions | *"What do real buyers ask when looking for recommendations, best picks, or advice in {category} in {geo}?"* | ChatGPT, Google AIO, Gemini, Perplexity |
| **2. Interest** | Test brand entity authority, catalog, specs & pricing | *"What prompts do users submit to check {Brand}'s catalog, specifications, features, and price range?"* | ChatGPT, Google AIO, Gemini, Perplexity |
| **3. Consideration** | Benchmark direct head-to-head positioning & unbiased reviews | *"What head-to-head comparison prompts (e.g. {Brand} vs {Competitor}) and review inquiries do consumers ask?"* | ChatGPT, Google AIO, Gemini, Perplexity |
| **4. Purchase** | Audit official store presence, dealer network, warranties, promos | *"What prompts do buyers submit when ready to purchase (where to buy, official stores, warranties, subsidies, financing)?"* | ChatGPT, Google AIO, Gemini, Perplexity |
| **5. After-Purchase** | Audit post-purchase support, durability & maintenance | *"What prompts do owners ask regarding maintenance, common problems, durability, and troubleshooting for {Brand}?"* | ChatGPT, Google AIO, Gemini, Perplexity |

---

## Interview & Execution Protocol

1. **Trigger Interactive Question Popup (`AskUserQuestion`)**: In Step 1, invoke the interactive question tool (`AskUserQuestion`) with structured questions (Brand & Scope, Competitors, Target Audience & USPs) offering smart defaults + custom text input fields (`Other`).
2. **Hard Stop**: Stop your turn immediately on the interactive question tool call and wait for the client's answers.
3. **Execute AI Reverse-Prompting (Step 1.5)**: Reverse-prompt ChatGPT / Gemini to extract authentic user queries into `queries.json`, then execute the live batch audit and aggregate quantitative metrics into `metrics.json`.
4. **Architect Slides (Step 2)**: Present the narrative architecture populated with real audit metrics and ask for approval via `AskUserQuestion`.
