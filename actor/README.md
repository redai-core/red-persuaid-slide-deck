# AI Search & Citation Scraper (Apify Actor)

Stealth headless browser scraper for **ChatGPT** (`chatgpt.com`) and **Google Gemini** (`gemini.google.com/app`). Built on **Camoufox** (stealth patched Firefox) with an X11 virtual display (`xvfb`) and **Apify Residential Proxies** to accurately scrape real search queries, live AI streaming responses, citation chips, and brand visibility metrics without getting blocked.

---

## 🚀 Features

- **Stealth Browser Automation**: Uses Camoufox to bypass Cloudflare Turnstile and anti-bot fingerprinting.
- **Dual AI Engine Support**:
  - `chatgpt`: Scrapes real ChatGPT web interface, citation sources, and external links.
  - `gemini`: Scrapes Google Gemini web app, source chips, and grounding links.
- **GEO & Brand Metrics**: Automatically calculates:
  - Brand Presence Rate (% of queries mentioning target brand)
  - Official Domain Citation Rate (% of queries citing official domain)
  - Competitor Share-of-Voice / Mention counts
  - Top 10 Cited Domains / Sources
- **Live Dataset Streaming**: Pushes results to the default Apify Dataset query-by-query.
- **Residential Proxy Support**: Built-in integration with Apify Residential Proxy pool.

---

## 📥 Input Schema

| Field | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `queries` | `Array<string>` | **Yes** | List of search queries to test | `["Apa rekomendasi motor listrik terbaik?"]` |
| `platform` | `string` | No | Target AI platform (`chatgpt` or `gemini`) | `"chatgpt"` |
| `brand_name` | `string` | No | Target brand name to monitor (e.g. `Electrum`) | `""` |
| `brand_domain` | `string` | No | Official brand domain (e.g. `electrum.id`) | `""` |
| `competitors` | `Array<string>` | No | Competitor brands to track (e.g. `["Alva", "Gesits"]`) | `[]` |
| `proxyConfiguration` | `object` | No | Apify proxy configuration (Residential recommended) | `{"useApifyProxy": true, "apifyProxyGroups": ["RESIDENTIAL"]}` |
| `delayBetweenQueries` | `integer` | No | Delay in seconds between consecutive queries | `3` |

### Sample JSON Input

```json
{
  "queries": [
    "Apa saja rekomendasi sepeda motor listrik terbaik di Indonesia?",
    "Bagaimana perbandingan motor listrik Electrum H5 vs Alva One?",
    "Berapa harga motor listrik Gesits terbaru 2024?"
  ],
  "platform": "chatgpt",
  "brand_name": "Electrum",
  "brand_domain": "electrum.id",
  "competitors": ["Alva", "Gesits"],
  "delayBetweenQueries": 3,
  "proxyConfiguration": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  }
}
```

---

## 📤 Output Format

### Dataset Items (Per Query)

```json
{
  "platform": "chatgpt",
  "query": "Bagaimana perbandingan motor listrik Electrum H5 vs Alva One?",
  "brand_name": "Electrum",
  "brand_domain": "electrum.id",
  "brand_cited": true,
  "brand_domain_cited": true,
  "competitors_mentioned": ["Alva"],
  "citations": [
    {
      "url": "https://electrum.id/products/h5",
      "domain": "electrum.id",
      "position": 1,
      "is_brand_domain": true
    },
    {
      "url": "https://alvaauto.com/one",
      "domain": "alvaauto.com",
      "position": 2,
      "is_brand_domain": false
    }
  ],
  "citation_domains": ["electrum.id", "alvaauto.com"],
  "raw_response_text": "Berikut adalah perbandingan antara Electrum H5 dan Alva One...",
  "response_length": 1420,
  "duration_seconds": 12.4,
  "timestamp": "2026-08-25T08:30:00.000Z",
  "error": null
}
```

### Key-Value Store `OUTPUT` (Summary)

```json
{
  "platform": "chatgpt",
  "brand_name": "Electrum",
  "brand_domain": "electrum.id",
  "total_queries_audited": 3,
  "brand_presence_count": 3,
  "brand_presence_rate_pct": 100.0,
  "brand_domain_citation_count": 2,
  "brand_domain_citation_rate_pct": 66.7,
  "competitor_mentions": {
    "Alva": 2,
    "Gesits": 1
  },
  "top_citation_sources": [
    {"domain": "electrum.id", "citations": 3},
    {"domain": "alvaauto.com", "citations": 2}
  ],
  "successful_audits": 3,
  "failed_audits": 0
}
```

---

## 🛠️ Local Development & Testing

### 1. Prerequisites
- Python 3.11+
- Apify CLI (`npm install -g apify-cli`)
- Docker (optional, for container testing)

### 2. Run Locally with Apify CLI
```bash
cd actor
apify login
apify run -p
```

### 3. Build & Test via Docker
```bash
cd actor
docker build -t ai-search-scraper .
docker run --rm -it ai-search-scraper
```

---

## 🚢 Deploy to Apify Cloud

```bash
cd actor
apify login
apify push
```

Once deployed, your actor will be available at:
`https://console.apify.com/actors/<your-username>/ai-search-citation-scraper`

---

## 💻 Calling via Apify API (Python)

```python
from apify_client import ApifyClient

client = ApifyClient("your_apify_token")

run_input = {
    "queries": [
        "Apa rekomendasi motor listrik terbaik?",
        "Perbandingan Electrum vs Alva"
    ],
    "platform": "chatgpt",
    "brand_name": "Electrum",
    "brand_domain": "electrum.id",
    "competitors": ["Alva", "Gesits"]
}

# Start the actor and wait for it to finish
run = client.actor("your-username/ai-search-citation-scraper").call(run_input=run_input)

# Fetch dataset results
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"Query: {item['query']} | Brand Cited: {item['brand_cited']}")
```
