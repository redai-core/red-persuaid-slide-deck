#!/usr/bin/env python3
"""
PersuAId Apify Cloud Integration Engine
Multi-provider cloud AI search, Google AI Overviews, and reverse-prompting engine:
- Gemini / Google: apify/google-ai-overviews-scraper (High-reliability SERP SGE scraping & citations)
- ChatGPT: calming_monument/ai-search-citation-scraper (Camoufox stealth with residential proxies)
- Fallback & Reverse-Prompting: fayoussef/bulk-llm-runner

Uses standard library urllib (zero external pip dependencies).
"""

import json
import os
import ssl
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from engine.models import AuditResult, Citation
from engine.credentials import resolve_apify_token


class ApifyClient:
    ACTOR_ID_BULK = "fayoussef~bulk-llm-runner"
    ACTOR_ID_GOOGLE_OVERVIEWS = "apify~google-ai-overviews-scraper"
    ACTOR_ID_CHATGPT_STEALTH = "calming_monument~ai-search-citation-scraper"
    BASE_URL = "https://api.apify.com/v2"

    MODEL_MAP = {
        "chatgpt": "openai/gpt-4o-mini",
        "gemini": "google/gemini-2.5-flash",
        "google": "google/gemini-2.5-flash",
        "perplexity": "perplexity/sonar",
    }

    def __init__(self, token: Optional[str] = None):
        self.token = resolve_apify_token(token)
        if not self.token:
            raise ValueError(
                "Apify token not found. Please provide your Apify API token (starts with 'apify_api_') "
                "via --apify-token, the APIFY_TOKEN environment variable, or store it in ~/.persuaid/credentials.json."
            )
        self.ssl_context = ssl._create_unverified_context()

    def _http_request(self, url: str, method: str = "GET", data: Optional[dict] = None) -> Any:
        full_url = f"{url}?token={self.token}" if "?" not in url else f"{url}&token={self.token}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps(data).encode("utf-8") if data is not None else None

        req = urllib.request.Request(full_url, data=payload, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body or str(e)
            raise RuntimeError(f"Apify API Error ({e.code}): {msg}")

    def run_actor_and_get_dataset(self, actor_id: str, input_payload: dict, timeout_seconds: int = 360) -> List[dict]:
        """Starts an actor run, polls until completion, and returns the dataset items."""
        start_url = f"{self.BASE_URL}/acts/{actor_id}/runs"
        run_res = self._http_request(start_url, method="POST", data=input_payload)
        run_data = run_res.get("data", {})
        run_id = run_data.get("id")
        dataset_id = run_data.get("defaultDatasetId")

        if not run_id or not dataset_id:
            raise RuntimeError(f"Failed to start Apify actor {actor_id}: {run_res}")

        # Poll for completion
        status_url = f"{self.BASE_URL}/actor-runs/{run_id}"
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            time.sleep(3)
            status_res = self._http_request(status_url, method="GET")
            status = status_res.get("data", {}).get("status")
            if status == "SUCCEEDED":
                dataset_url = f"{self.BASE_URL}/datasets/{dataset_id}/items"
                items = self._http_request(dataset_url, method="GET")
                return items if isinstance(items, list) else []
            elif status in ["FAILED", "TIMED-OUT", "ABORTED"]:
                raise RuntimeError(f"Apify actor {actor_id} run {run_id} failed with status: {status}")

        raise TimeoutError(f"Apify actor {actor_id} run {run_id} timed out after {timeout_seconds}s")

    def reverse_prompt(self, platform: str, meta_prompt: str) -> str:
        """Sends the reverse-prompting meta-prompt to ChatGPT or Gemini model via bulk-llm-runner."""
        model_name = self.MODEL_MAP.get(platform.lower(), "openai/gpt-4o-mini")
        payload = {
            "prompts": [meta_prompt],
            "model": model_name,
            "enable_web_search": False,
            "max_tokens": 1500,
        }
        items = self.run_actor_and_get_dataset(self.ACTOR_ID_BULK, payload)
        if not items:
            return ""
        first_item = items[0]
        return first_item.get("response", first_item.get("text", ""))

    def audit_gemini_overviews(self, queries: List[str], brand_name: str, chunk_size: int = 50) -> List[AuditResult]:
        """
        Audits Gemini/Google search presence via apify/google-ai-overviews-scraper in a single batched run.
        Extracts Google AI Overview text and source citations with zero login wall issues.
        """
        all_results: List[AuditResult] = []

        for i in range(0, len(queries), chunk_size):
            chunk = queries[i : i + chunk_size]
            payload = {
                "queries": "\n".join(chunk)
            }
            try:
                timeout = max(180, len(chunk) * 30)
                items = self.run_actor_and_get_dataset(self.ACTOR_ID_GOOGLE_OVERVIEWS, payload, timeout_seconds=timeout)
                # Map items by query for accurate ordering
                item_by_query = {item.get("query", "").strip().lower(): item for item in items}

                for q in chunk:
                    matched = item_by_query.get(q.strip().lower())
                    if not matched:
                        # Fallback to first available or empty
                        matched = items.pop(0) if items else {}

                    resp_text = matched.get("text", "")
                    raw_sources = matched.get("sources", [])
                    citations: List[Citation] = []

                    for s in raw_sources:
                        if isinstance(s, dict):
                            u = s.get("url")
                            t = s.get("title")
                        else:
                            u = str(s)
                            t = None
                        if u and u.startswith("http"):
                            citations.append(Citation.from_url(u, title=t))

                    # Deduplicate citations by URL
                    seen = set()
                    unique_citations = []
                    for c in citations:
                        if c.url not in seen:
                            seen.add(c.url)
                            unique_citations.append(c)

                    brand_cited = brand_name.lower() in resp_text.lower() if brand_name else False

                    res = AuditResult(
                        platform="gemini",
                        account_id="apify_google_ai_overviews",
                        query=q,
                        brand_name=brand_name,
                        brand_cited=brand_cited,
                        citations=unique_citations,
                        raw_response_text=resp_text,
                        response_length=len(resp_text),
                        duration_seconds=4.0,
                    )
                    all_results.append(res)
            except Exception as e:
                print(f"        ⚠️ Gemini/Google Overview scraping error on chunk {i//chunk_size + 1}: {e}")
                raise e

        return all_results

    def audit_chatgpt(
        self,
        queries: List[str],
        brand_name: str,
        brand_domain: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        chunk_size: int = 50,
    ) -> List[AuditResult]:
        """
        Audits ChatGPT responses using fast, search-grounded cloud LLM runner (fayoussef/bulk-llm-runner).
        Note: Browser-based Camoufox scraper is disabled to eliminate latency and timeout bottlenecks.
        """
        all_results: List[AuditResult] = []

        for i in range(0, len(queries), chunk_size):
            chunk = queries[i : i + chunk_size]
            payload = {
                "prompts": chunk,
                "model": "openai/gpt-4o-mini",
                "enable_web_search": True,
                "max_tokens": 1200,
            }
            timeout = max(120, len(chunk) * 15)
            items = self.run_actor_and_get_dataset(self.ACTOR_ID_BULK, payload, timeout_seconds=timeout)
            for item in items:
                q_text = item.get("prompt", item.get("query", ""))
                resp_text = item.get("response", item.get("text", ""))
                raw_sources = item.get("annotations", item.get("sources", item.get("citations", [])))
                citations = []
                for s in raw_sources:
                    u = s.get("url") if isinstance(s, dict) else str(s)
                    if u and u.startswith("http"):
                        citations.append(Citation.from_url(u))

                brand_cited = brand_name.lower() in resp_text.lower() if brand_name else False
                res = AuditResult(
                    platform="chatgpt",
                    account_id="apify_chatgpt_search",
                    query=q_text,
                    brand_name=brand_name,
                    brand_cited=brand_cited,
                    citations=citations,
                    raw_response_text=resp_text,
                    response_length=len(resp_text),
                    duration_seconds=3.0,
                )
                all_results.append(res)

        return all_results

    def batch_audit(self, platform: str, queries: List[str], brand_name: str) -> List[AuditResult]:
        """
        Dispatches batch audits to the optimal Apify Actor for the given platform.
        - 'gemini' / 'google': Uses apify/google-ai-overviews-scraper
        - 'chatgpt': Uses calming_monument/ai-search-citation-scraper (with bulk-llm fallback)
        - 'perplexity': Uses bulk-llm-runner
        """
        plat = platform.lower().strip()
        if plat in ["gemini", "google"]:
            return self.audit_gemini_overviews(queries=queries, brand_name=brand_name)
        elif plat == "chatgpt":
            return self.audit_chatgpt(queries=queries, brand_name=brand_name)
        else:
            # Generic model search
            model_name = self.MODEL_MAP.get(plat, "openai/gpt-4o-mini")
            chunk_size = 3
            all_items = []
            for i in range(0, len(queries), chunk_size):
                chunk = queries[i : i + chunk_size]
                payload = {
                    "prompts": chunk,
                    "model": model_name,
                    "enable_web_search": True,
                    "max_tokens": 1200,
                }
                items = self.run_actor_and_get_dataset(self.ACTOR_ID_BULK, payload)
                if items:
                    all_items.extend(items)

            results = []
            for item in all_items:
                q_text = item.get("prompt", item.get("query", ""))
                resp_text = item.get("response", item.get("text", ""))
                raw_sources = item.get("annotations", item.get("sources", item.get("citations", [])))
                citations = [Citation.from_url(s.get("url") if isinstance(s, dict) else str(s)) for s in raw_sources if (s.get("url") if isinstance(s, dict) else str(s)).startswith("http")]
                brand_cited = brand_name.lower() in resp_text.lower() if brand_name else False
                results.append(
                    AuditResult(
                        platform=plat,
                        account_id="apify_bulk_llm",
                        query=q_text,
                        brand_name=brand_name,
                        brand_cited=brand_cited,
                        citations=citations,
                        raw_response_text=resp_text,
                        response_length=len(resp_text),
                        duration_seconds=3.0,
                    )
                )
            return results
