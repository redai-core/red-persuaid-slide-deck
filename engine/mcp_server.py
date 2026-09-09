#!/usr/bin/env python3
"""
PersuAId Local MCP (Model Context Protocol) Server
Exposes PersuAId's multi-platform GEO audit engine, query formatter, metric aggregator,
and secure credentials manager as standardized MCP tools over stdio.

Runs with pure Python standard library (zero external pip dependencies).
Compatible with all MCP clients: ZCode, Claude Desktop, Cursor, Zed, Goose, Roo Code.
Includes asynchronous job dispatching, in-flight deduplication, and result caching.
"""

import sys
import os
import json
import logging
import hashlib
import time
import threading
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure stderr logging (keeping stdout clean for JSON-RPC 2.0 communication)
logging.basicConfig(
    level=logging.INFO,
    format="[persuaid-mcp] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("persuaid-mcp")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.credentials import resolve_apify_token, store_token, get_stored_token, has_apify_token
from engine.apify_client import ApifyClient
from scripts.format_queries import (
    reverse_prompt_queries,
    generate_platform_journey_queries,
    sample_audit_queries,
    export_itemized_csv,
    export_matrix_csv,
)
from scripts.aggregate_metrics import aggregate_audit_results
from scripts.run_audit_pipeline import run_pipeline


SERVER_INFO = {
    "name": "persuaid-mcp",
    "version": "1.4.0",
}

SERVER_CAPABILITIES = {
    "tools": {},
    "resources": {},
}

_GENERATED_DECKS: Dict[str, Path] = {}

TOOLS = [
    {
        "name": "persuaid_start_pipeline",
        "description": "Starts the complete Step 1.5 GEO audit pipeline in the background and returns immediately with a job_id (<1s response). Zero risk of client timeouts. Check progress and retrieve results via persuaid_get_pipeline_status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name (e.g. 'Siloam International Hospital', 'Electrum').",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category (e.g. 'healthcare network', 'motor listrik').",
                },
                "competitors": {
                    "type": "string",
                    "description": "Comma-separated list of top benchmark competitors.",
                },
                "geo": {
                    "type": "string",
                    "default": "Indonesia",
                    "description": "Geographic market (e.g. 'Indonesia', 'Global').",
                },
                "domain": {
                    "type": "string",
                    "description": "Official brand website domain (e.g. 'siloamhospitals.com').",
                },
                "platform": {
                    "type": "string",
                    "default": "chatgpt,gemini",
                    "description": "Target AI platforms ('chatgpt', 'gemini', or 'chatgpt,gemini').",
                },
                "samples_per_stage": {
                    "type": "integer",
                    "default": 1,
                    "description": "Number of sample queries to audit per stage (default: 1).",
                },
                "generate_deck": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to automatically compile the 21-slide Redcomm executive GEO pitch deck (.pptx).",
                },
            },
            "required": ["brand", "category", "competitors"],
        },
    },
    {
        "name": "persuaid_get_pipeline_status",
        "description": "Polls the status of an active or completed background GEO audit job. When status is 'completed', returns the full metrics object, Share of Voice %, and CSV prompt taxonomy contents inline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "The job_id returned by persuaid_start_pipeline.",
                },
                "brand": {
                    "type": "string",
                    "description": "Optional brand name to find the latest job if job_id is omitted.",
                },
            },
        },
    },
    {
        "name": "persuaid_run_pipeline",
        "description": "Runs the complete Step 1.5 GEO audit pipeline synchronously (blocking). Generates 5-stage search journey query taxonomy, exports CSV matrix, audits ChatGPT and Gemini via cloud Apify actors in parallel, and returns comprehensive metrics and CSV content inline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name.",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category.",
                },
                "competitors": {
                    "type": "string",
                    "description": "Comma-separated list of top competitors.",
                },
                "geo": {
                    "type": "string",
                    "default": "Indonesia",
                    "description": "Geographic market.",
                },
                "domain": {
                    "type": "string",
                    "description": "Official brand website domain.",
                },
                "platform": {
                    "type": "string",
                    "default": "chatgpt,gemini",
                    "description": "Target AI platforms.",
                },
                "samples_per_stage": {
                    "type": "integer",
                    "default": 1,
                    "description": "Number of sample queries per stage (default: 1).",
                },
                "generate_deck": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to automatically compile the 21-slide Redcomm executive GEO pitch deck (.pptx).",
                },
            },
            "required": ["brand", "category", "competitors"],
        },
    },
    {
        "name": "persuaid_generate_deck",
        "description": "Compiles a complete 21-slide Redcomm executive GEO pitch deck (.pptx) using pure code generation from metrics.json or brand parameters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name (e.g. 'Auto2000', 'Electrum').",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category (e.g. 'authorized Toyota dealer', 'motor listrik').",
                },
                "competitors": {
                    "type": "string",
                    "default": "Competitor A, Competitor B",
                    "description": "Comma-separated list of top competitors.",
                },
                "domain": {
                    "type": "string",
                    "description": "Official brand website domain (optional).",
                },
                "metrics_path": {
                    "type": "string",
                    "description": "Optional path to metrics.json or otterly_intel.json from an audit run.",
                },
                "metrics_data": {
                    "type": "object",
                    "description": "Optional inline metrics JSON object from Otterly or Apify audit (avoids filesystem path mismatches when running over remote MCP).",
                },
                "out_dir": {
                    "type": "string",
                    "default": ".",
                    "description": "Output directory for the generated .pptx presentation.",
                },
                "year": {
                    "type": "integer",
                    "default": 2026,
                    "description": "Target strategy year (default: 2026).",
                },
            },
            "required": ["brand", "category"],
        },
    },
    {
        "name": "persuaid_audit_query",
        "description": "Audits a single search query on ChatGPT, Google Gemini (AI Overviews), or both to evaluate brand presence, citation domains, and competitor mentions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search prompt or question to audit.",
                },
                "platform": {
                    "type": "string",
                    "enum": ["chatgpt", "gemini", "all"],
                    "default": "chatgpt",
                    "description": "Target AI platform ('chatgpt', 'gemini', or 'all').",
                },
                "brand_name": {
                    "type": "string",
                    "description": "The client brand name to track for presence and citations.",
                },
                "brand_domain": {
                    "type": "string",
                    "description": "The client website domain.",
                },
                "competitors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of competitor brand names to detect.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "persuaid_format_queries",
        "description": "Generates a structured 5-stage AI Search Journey query taxonomy (Discovery, Interest, Consideration, Purchase, After-Purchase) across ChatGPT and Gemini.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name.",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category.",
                },
                "competitors": {
                    "type": "string",
                    "description": "Comma-separated list of competitors.",
                },
                "geo": {
                    "type": "string",
                    "default": "Indonesia",
                    "description": "Geographic scope.",
                },
            },
            "required": ["brand", "category", "competitors"],
        },
    },
    {
        "name": "persuaid_aggregate_metrics",
        "description": "Computes analytical GEO benchmarks (Share of Voice %, #1 recommendation Win Rate %, 5-stage funnel visibility, citation domains) from audit results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "results_file": {
                    "type": "string",
                    "description": "Path to results.json or raw list of audit items.",
                },
                "brand": {
                    "type": "string",
                    "description": "Target brand name.",
                },
                "brand_domain": {
                    "type": "string",
                    "description": "Optional official website domain.",
                },
            },
            "required": ["results_file", "brand"],
        },
    },
    {
        "name": "persuaid_configure_credentials",
        "description": "Checks, tests, or configures the Apify API token stored securely in ~/.persuaid/credentials.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "apify_token": {
                    "type": "string",
                    "description": "Apify API token (starts with apify_api_...). If omitted, checks existing credentials.",
                },
                "test_connection": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to test the token validity against Apify API.",
                },
            },
        },
    },
    {
        "name": "persuaid_learn_template",
        "description": "Decompiles any user-uploaded PowerPoint presentation (.pptx), extracts its unit-space physical geometry [0.0, 1.0], color palette tokens, typography scale, recurring chrome, and layout archetypes, returning a compact ~300-token Archetype Menu for presentation staging.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_path": {
                    "type": "string",
                    "description": "Local filesystem path to the user-uploaded reference .pptx file.",
                },
                "template_id": {
                    "type": "string",
                    "description": "Optional custom identifier for the learned template.",
                },
                "name": {
                    "type": "string",
                    "description": "Optional human-readable name for the template.",
                },
            },
            "required": ["template_path"],
        },
    },
    {
        "name": "persuaid_init_session",
        "description": "Initializes an interactive Act-by-Act presentation staging workspace with target brand parameters, total slide count, and template profile.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "The client brand name (e.g. 'Auto2000', 'Siloam Hospitals').",
                },
                "category": {
                    "type": "string",
                    "description": "Product or service category (e.g. 'authorized Toyota dealer & service network').",
                },
                "template_id_or_path": {
                    "type": "string",
                    "description": "Optional template ID, custom profile JSON path, or reference .pptx path. Defaults to Redcomm Executive theme.",
                },
                "competitors": {
                    "type": "string",
                    "default": "Competitor A, Competitor B",
                    "description": "Comma-separated list of top competitors.",
                },
                "domain": {
                    "type": "string",
                    "description": "Official brand website domain.",
                },
                "total_slides": {
                    "type": "integer",
                    "default": 21,
                    "description": "Target total presentation slide count (e.g. 8, 12, 16, 21).",
                },
            },
            "required": ["brand", "category"],
        },
    },
    {
        "name": "persuaid_get_archetypes",
        "description": "Retrieves lightweight slot schemas (~200 tokens) and character budget constraints for slide archetypes recommended for a specific consulting Act (e.g. 'Act I', 'Act II').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active staging session ID returned by persuaid_init_session.",
                },
                "act": {
                    "type": "string",
                    "description": "The consulting act name (e.g. 'Act I', 'Act II', 'Act III', 'Act IV').",
                },
            },
            "required": ["session_id", "act"],
        },
    },
    {
        "name": "persuaid_stage_act",
        "description": "Stages 3 to 5 slides grouped by consulting Act into the active session. Immediately validates text against physical container character limits to prevent visual text overflow.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active staging session ID.",
                },
                "act": {
                    "type": "string",
                    "description": "The consulting act name (e.g. 'Act I', 'Act II', 'Act III', 'Act IV').",
                },
                "slides": {
                    "type": "array",
                    "description": "List of slide specifications to stage, each containing slide_number, archetype_id, and slots dictionary.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "slide_number": {"type": "integer"},
                            "archetype_id": {"type": "string"},
                            "slots": {"type": "object"},
                            "notes": {"type": "string"},
                        },
                        "required": ["slide_number", "archetype_id", "slots"],
                    },
                },
            },
            "required": ["session_id", "act", "slides"],
        },
    },
    {
        "name": "persuaid_compile_session",
        "description": "Compiles all staged slides in the session into a native, fully editable OpenXML PowerPoint presentation (.pptx) adhering to the learned visual template tokens and geometry.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active staging session ID.",
                },
                "out_dir": {
                    "type": "string",
                    "default": ".",
                    "description": "Output directory for the compiled .pptx presentation.",
                },
            },
            "required": ["session_id"],
        },
    },
]


# ==============================================================================
# Idempotency, In-Flight Deduplication, and Background Job Registry
# ==============================================================================

_RESULT_CACHE: Dict[str, tuple] = {}
_IN_FLIGHT: Dict[str, tuple] = {}
_PIPELINE_JOBS: Dict[str, Dict[str, Any]] = {}
_IDEMPOTENCY_LOCK = threading.Lock()
_JOBS_LOCK = threading.Lock()
CACHE_TTL_SECONDS = 7200  # 2 hours


def _get_cache_key(prefix: str, data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def handle_persuaid_audit_query(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args["query"]
    platform = args.get("platform", "chatgpt").lower()
    brand_name = args.get("brand_name", "")
    brand_domain = args.get("brand_domain", "")

    cache_key = _get_cache_key("audit", {
        "query": query.strip().lower(),
        "platform": platform,
        "brand_name": brand_name.strip().lower(),
        "brand_domain": brand_domain.strip().lower(),
    })

    now = time.time()

    with _IDEMPOTENCY_LOCK:
        if cache_key in _RESULT_CACHE:
            ts, cached_res = _RESULT_CACHE[cache_key]
            if now - ts < CACHE_TTL_SECONDS:
                logger.info(f"⚡ [IDEMPOTENT] Returning cached audit result for key: {cache_key}")
                return cached_res

        if cache_key in _IN_FLIGHT:
            event, container = _IN_FLIGHT[cache_key]
            is_worker = False
        else:
            event = threading.Event()
            container = {}
            _IN_FLIGHT[cache_key] = (event, container)
            is_worker = True

    if not is_worker:
        logger.info(f"⏳ [IN-FLIGHT DEDUP] Waiting for existing audit run: {cache_key}")
        event.wait(timeout=180)
        return container.get("result", {"status": "error", "error": "In-flight audit timed out."})

    try:
        token = resolve_apify_token()
        if not token:
            res_val = {"error": "Apify token not found. Please run persuaid_configure_credentials to set your Apify API token."}
            container["result"] = res_val
            return res_val

        client = ApifyClient(token=token)
        platforms_to_audit = ["chatgpt", "gemini"] if platform == "all" else [platform]

        results_data = []
        for plat in platforms_to_audit:
            try:
                if plat == "gemini":
                    res = client.audit_gemini_overviews(queries=[query], brand_name=brand_name)
                else:
                    res = client.audit_chatgpt(queries=[query], brand_name=brand_name)

                for r in res:
                    if hasattr(r, "to_dict"):
                        results_data.append(r.to_dict())
                    elif hasattr(r, "model_dump"):
                        results_data.append(r.model_dump(mode="json"))
                    elif isinstance(r, dict):
                        results_data.append(r)
                    else:
                        results_data.append(vars(r))
            except Exception as e:
                logger.error(f"Error auditing {plat} query: {e}")
                results_data.append({
                    "platform": plat,
                    "query": query,
                    "error": str(e),
                })

        final_res = {
            "status": "success",
            "query": query,
            "results": results_data,
        }

        container["result"] = final_res
        with _IDEMPOTENCY_LOCK:
            _RESULT_CACHE[cache_key] = (time.time(), final_res)
        return final_res

    finally:
        with _IDEMPOTENCY_LOCK:
            event.set()
            _IN_FLIGHT.pop(cache_key, None)


def handle_persuaid_run_pipeline(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    competitors = args["competitors"]
    geo = args.get("geo", "Indonesia")
    domain = args.get("domain")
    platform = args.get("platform", "chatgpt,gemini")
    out_dir = args.get("out_dir", "/tmp/persuaid_runs")
    samples_per_stage = args.get("samples_per_stage", 1)
    reverse_prompt = args.get("reverse_prompt", True)
    generate_deck = args.get("generate_deck", False)
    brand_slug = brand.strip().replace(" ", "_")

    cache_key = _get_cache_key("pipeline", {
        "brand": brand.strip().lower(),
        "domain": (domain or "").strip().lower(),
        "category": category.strip().lower(),
        "competitors": sorted([c.strip().lower() for c in competitors.split(",") if c.strip()]),
        "geo": geo.strip().lower(),
        "platform": platform.strip().lower(),
        "samples_per_stage": samples_per_stage,
        "generate_deck": generate_deck,
    })

    now = time.time()

    with _IDEMPOTENCY_LOCK:
        if cache_key in _RESULT_CACHE:
            ts, cached_res = _RESULT_CACHE[cache_key]
            if now - ts < CACHE_TTL_SECONDS:
                logger.info(f"⚡ [IDEMPOTENT] Returning cached pipeline result for: {brand} ({cache_key})")
                return cached_res

        if cache_key in _IN_FLIGHT:
            event, container = _IN_FLIGHT[cache_key]
            is_worker = False
        else:
            event = threading.Event()
            container = {}
            _IN_FLIGHT[cache_key] = (event, container)
            is_worker = True

    if not is_worker:
        logger.info(f"⏳ [IN-FLIGHT DEDUP] Waiting on active cloud run for '{brand}' ({cache_key})...")
        event.wait(timeout=180)
        return container.get("result", {"status": "error", "error": "In-flight pipeline run timed out."})

    try:
        pipeline_output = run_pipeline(
            brand=brand,
            category=category,
            competitors=competitors,
            geo=geo,
            domain=domain,
            platform=platform,
            out_dir=out_dir,
            reverse_prompt=reverse_prompt,
            samples_per_stage=samples_per_stage,
            provider="auto",
            generate_deck=generate_deck,
        )

        metrics = pipeline_output.get("metrics") if isinstance(pipeline_output, dict) else pipeline_output
        csv_itemized = pipeline_output.get("csv_itemized_content", "") if isinstance(pipeline_output, dict) else ""
        csv_matrix = pipeline_output.get("csv_matrix_content", "") if isinstance(pipeline_output, dict) else ""
        deck_path = pipeline_output.get("deck_path") if isinstance(pipeline_output, dict) else None

        final_res = {
            "status": "success",
            "message": f"GEO audit pipeline completed successfully for {brand}.",
            "brand": brand,
            "domain": domain,
            "category": category,
            "metrics": metrics,
            "deck_path": deck_path,
            "csv_itemized_content": csv_itemized,
            "csv_matrix_content": csv_matrix,
            "itemized_csv_filename": f"{brand_slug}_AI_Search_Journey_Prompts.csv",
            "matrix_csv_filename": f"{brand_slug}_AI_Search_Journey_Matrix.csv",
            "total_queries_audited": len(pipeline_output.get("results", [])) if isinstance(pipeline_output, dict) else 0,
        }

        container["result"] = final_res
        with _IDEMPOTENCY_LOCK:
            _RESULT_CACHE[cache_key] = (time.time(), final_res)
        return final_res

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        err_res = {
            "status": "error",
            "error": str(e),
        }
        container["result"] = err_res
        return err_res

    finally:
        with _IDEMPOTENCY_LOCK:
            event.set()
            _IN_FLIGHT.pop(cache_key, None)


def handle_persuaid_start_pipeline(args: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronously starts the GEO audit pipeline and returns immediately (<0.2s)."""
    brand = args["brand"]
    category = args["category"]
    competitors = args["competitors"]
    geo = args.get("geo", "Indonesia")
    domain = args.get("domain")
    platform = args.get("platform", "chatgpt,gemini")
    samples_per_stage = args.get("samples_per_stage", 1)

    canonical_key = _get_cache_key("pipeline", {
        "brand": brand.strip().lower(),
        "domain": (domain or "").strip().lower(),
        "category": category.strip().lower(),
        "competitors": sorted([c.strip().lower() for c in competitors.split(",") if c.strip()]),
        "geo": geo.strip().lower(),
        "platform": platform.strip().lower(),
        "samples_per_stage": samples_per_stage,
    })

    now = time.time()

    # 1. If result is already cached, return ready
    with _IDEMPOTENCY_LOCK:
        if canonical_key in _RESULT_CACHE:
            ts, cached_res = _RESULT_CACHE[canonical_key]
            if now - ts < CACHE_TTL_SECONDS:
                job_id = f"job_{canonical_key.split(':')[1][:10]}"
                with _JOBS_LOCK:
                    _PIPELINE_JOBS[job_id] = {
                        "job_id": job_id,
                        "cache_key": canonical_key,
                        "status": "completed",
                        "brand": brand,
                        "start_time": ts,
                        "duration_seconds": 0.05,
                        "result": cached_res,
                        "progress": "Loaded from cache.",
                    }
                return {
                    "status": "completed",
                    "job_id": job_id,
                    "brand": brand,
                    "ready": True,
                    "message": f"Audit already completed for {brand}. Call persuaid_get_pipeline_status with job_id '{job_id}' to retrieve all data.",
                }

    # 2. If already running in background, return active job_id
    with _JOBS_LOCK:
        for j_id, j_data in _PIPELINE_JOBS.items():
            if j_data.get("cache_key") == canonical_key and j_data.get("status") == "running":
                elapsed = round(time.time() - j_data["start_time"], 1)
                return {
                    "status": "already_running",
                    "job_id": j_id,
                    "brand": brand,
                    "ready": False,
                    "elapsed_seconds": elapsed,
                    "message": f"Audit for {brand} is actively executing in background ({elapsed}s elapsed). Check status via persuaid_get_pipeline_status.",
                }

    # 3. Create fresh background job
    job_id = f"job_{uuid.uuid4().hex[:10]}"
    job_event = threading.Event()
    job_record = {
        "job_id": job_id,
        "cache_key": canonical_key,
        "brand": brand,
        "category": category,
        "status": "running",
        "progress": "Auditing ChatGPT and Google Gemini in parallel via Apify Cloud...",
        "start_time": time.time(),
        "event": job_event,
        "result": None,
        "error": None,
    }
    with _JOBS_LOCK:
        _PIPELINE_JOBS[job_id] = job_record

    def async_runner():
        try:
            res = handle_persuaid_run_pipeline(args)
            with _JOBS_LOCK:
                job_record["status"] = "completed" if res.get("status") == "success" else "error"
                job_record["duration_seconds"] = round(time.time() - job_record["start_time"], 1)
                job_record["result"] = res
                job_record["progress"] = "Audit completed successfully."
        except BaseException as ex:
            with _JOBS_LOCK:
                job_record["status"] = "error"
                job_record["error"] = str(ex)
                job_record["progress"] = f"Failed: {ex}"
        finally:
            job_event.set()

    threading.Thread(target=async_runner, daemon=True).start()

    return {
        "status": "started",
        "job_id": job_id,
        "brand": brand,
        "ready": False,
        "message": f"GEO audit pipeline launched in background. Call persuaid_get_pipeline_status(job_id='{job_id}') immediately (it will automatically wait until complete).",
    }


def handle_persuaid_get_pipeline_status(args: Dict[str, Any]) -> Dict[str, Any]:
    """Polls the status of a background GEO audit job with automatic server-side wait."""
    job_id = args.get("job_id", "").strip()
    brand = args.get("brand", "").strip().lower()
    wait_seconds = float(args.get("wait_seconds", 30.0))

    with _JOBS_LOCK:
        job = _PIPELINE_JOBS.get(job_id)
        if not job and brand:
            for j in reversed(list(_PIPELINE_JOBS.values())):
                if j.get("brand", "").lower() == brand:
                    job = j
                    break

        if not job:
            return {
                "status": "not_found",
                "ready": False,
                "error": f"No active or completed job found for job_id='{job_id}'. Call persuaid_start_pipeline to start an audit.",
            }

        status = job.get("status")
        job_event = job.get("event")

    # Long-polling: If still running, wait on the event for up to 35 seconds
    if status == "running" and job_event and wait_seconds > 0:
        logger.info(f"⏳ Server-side wait on job {job_id} for up to {wait_seconds}s...")
        job_event.wait(timeout=min(wait_seconds, 35.0))
        with _JOBS_LOCK:
            status = job.get("status")

    elapsed = round(time.time() - job["start_time"], 1)

    if status == "completed":
        res = job.get("result", {})
        return {
            "status": "completed",
            "job_id": job["job_id"],
            "brand": job["brand"],
            "ready": True,
            "duration_seconds": job.get("duration_seconds", elapsed),
            "metrics": res.get("metrics"),
            "deck_path": res.get("deck_path"),
            "csv_itemized_content": res.get("csv_itemized_content", ""),
            "csv_matrix_content": res.get("csv_matrix_content", ""),
            "itemized_csv_filename": res.get("itemized_csv_filename", ""),
            "matrix_csv_filename": res.get("matrix_csv_filename", ""),
            "total_queries_audited": res.get("total_queries_audited", 0),
        }

    elif status == "running":
        return {
            "status": "running",
            "job_id": job["job_id"],
            "brand": job["brand"],
            "ready": False,
            "elapsed_seconds": elapsed,
            "progress": job.get("progress", "Auditing search engines in parallel..."),
            "message": f"Audit is actively running ({elapsed}s elapsed).",
        }

    else:
        return {
            "status": "error",
            "job_id": job["job_id"],
            "ready": True,
            "error": job.get("error") or "Pipeline execution encountered an error.",
        }


def handle_persuaid_format_queries(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    competitors = args["competitors"]
    geo = args.get("geo", "Indonesia")
    out_file = args.get("out")

    comp_list = [c.strip() for c in competitors.split(",") if c.strip()] if isinstance(competitors, str) else competitors
    
    token = resolve_apify_token()
    queries = None
    if token:
        try:
            queries = reverse_prompt_queries(brand, category, comp_list, geo)
        except Exception as e:
            logger.warning(f"Reverse prompting failed, generating standard journey taxonomy: {e}")

    if not queries:
        queries = generate_platform_journey_queries(brand, category, comp_list, geo)

    if out_file:
        Path(out_file).write_text(json.dumps(queries, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "success",
        "brand": brand,
        "category": category,
        "total_queries": sum(len(q_list) for q_list in queries.values()) if isinstance(queries, dict) else len(queries),
        "taxonomy": queries,
    }


def handle_persuaid_aggregate_metrics(args: Dict[str, Any]) -> Dict[str, Any]:
    results_file = args["results_file"]
    brand = args["brand"]
    brand_domain = args.get("brand_domain")
    out_file = args.get("out")

    try:
        metrics = aggregate_audit_results(
            results=results_file,
            brand_name=brand,
            brand_domain=brand_domain,
        )
        if out_file and metrics and "error" not in metrics:
            Path(out_file).write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "status": "success",
            "metrics": metrics,
        }
    except Exception as e:
        logger.error(f"Error aggregating metrics: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def handle_persuaid_configure_credentials(args: Dict[str, Any]) -> Dict[str, Any]:
    new_token = args.get("apify_token")
    test_conn = args.get("test_connection", True)

    if new_token:
        store_token(new_token)
        token_to_use = new_token
        action_note = "New Apify token stored securely in ~/.persuaid/credentials.json (0600)."
    else:
        token_to_use = resolve_apify_token()
        action_note = "Using currently resolved Apify token."

    if not token_to_use:
        return {
            "status": "not_configured",
            "message": "No Apify token is currently configured. Provide 'apify_token' to authenticate.",
            "credentials_file": str(Path.home() / ".persuaid" / "credentials.json"),
        }

    token_masked = token_to_use[:10] + "..." + token_to_use[-4:] if len(token_to_use) > 15 else "***"
    conn_status = "untested"
    user_info = None

    if test_conn:
        try:
            import urllib.request
            req = urllib.request.Request(f"https://api.apify.com/v2/users/me?token={token_to_use}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())["data"]
                user_info = {
                    "username": data.get("username"),
                    "email": data.get("email"),
                    "plan": data.get("plan", {}).get("name"),
                }
                conn_status = "valid"
        except Exception as e:
            conn_status = f"invalid: {e}"

    return {
        "status": "configured",
        "action": action_note,
        "token_preview": token_masked,
        "connection_test": conn_status,
        "user_info": user_info,
        "credentials_file": str(Path.home() / ".persuaid" / "credentials.json"),
    }


def handle_persuaid_generate_deck(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    competitors = args.get("competitors", "Competitor A, Competitor B")
    domain = args.get("domain")
    metrics_path = args.get("metrics_path")
    metrics_data = args.get("metrics_data") or args.get("metrics")
    out_dir = args.get("out_dir", ".")
    year = int(args.get("year", 2026))

    try:
        import base64
        from engine.deckcraft.builder import compile_deck
        deck_path = compile_deck(
            brand=brand,
            category=category,
            competitors=competitors,
            domain=domain,
            metrics_path=metrics_path,
            metrics_data=metrics_data,
            out_dir=out_dir,
            year=year,
        )

        file_bytes = deck_path.read_bytes()
        file_size_kb = round(len(file_bytes) / 1024.0, 1)
        deck_b64 = base64.b64encode(file_bytes).decode("ascii")

        _GENERATED_DECKS[deck_path.name] = deck_path

        return {
            "status": "success",
            "brand": brand,
            "category": category,
            "filename": deck_path.name,
            "deck_path": str(deck_path),
            "file_size_kb": file_size_kb,
            "total_slides": 21,
            "deck_base64": deck_b64,
            "download_url": f"/download/{deck_path.name}",
            "message": f"Successfully compiled 21-slide Redcomm executive GEO pitch deck for {brand} ({file_size_kb} KB). Base64 payload provided in 'deck_base64' for direct writing to client workspace.",
        }
    except Exception as e:
        logger.exception(f"Failed to compile presentation deck for {brand}: {e}")
        return {
            "status": "error",
            "brand": brand,
            "error": str(e),
        }


def handle_persuaid_learn_template(args: Dict[str, Any]) -> Dict[str, Any]:
    template_path = args["template_path"]
    template_id = args.get("template_id")
    name = args.get("name")

    try:
        from engine.template_decompiler import TemplateDecompiler
        decompiler = TemplateDecompiler(template_path)
        profile = decompiler.decompile(template_id=template_id, name=name)

        return {
            "status": "success",
            "template_id": profile.template_id,
            "name": profile.name,
            "canvas": {
                "width_inches": profile.canvas.width_inches,
                "height_inches": profile.canvas.height_inches,
                "aspect_ratio": profile.canvas.aspect_ratio,
            },
            "palette": {
                "background": profile.palette.background,
                "accent_primary": profile.palette.accent_primary,
                "container_primary": profile.palette.container_primary,
            },
            "total_archetypes": len(profile.archetypes),
            "archetype_menu": profile.get_archetype_menu(),
            "message": f"Successfully decompiled template '{profile.name}'. Call persuaid_init_session to start staging slides.",
        }
    except Exception as e:
        logger.exception(f"Failed to learn template from {template_path}: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def handle_persuaid_init_session(args: Dict[str, Any]) -> Dict[str, Any]:
    brand = args["brand"]
    category = args["category"]
    template_id_or_path = args.get("template_id_or_path")
    competitors = args.get("competitors", "Competitor A, Competitor B")
    domain = args.get("domain")
    total_slides = int(args.get("total_slides", 21))

    try:
        from engine.staging_manager import DeckStagingManager
        mgr = DeckStagingManager()
        return mgr.create_session(
            brand=brand,
            category=category,
            template_id_or_path=template_id_or_path,
            competitors=competitors,
            domain=domain,
            total_slides=total_slides,
        )
    except Exception as e:
        logger.exception(f"Failed to init staging session for {brand}: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def handle_persuaid_get_archetypes(args: Dict[str, Any]) -> Dict[str, Any]:
    session_id = args["session_id"]
    act = args["act"]

    try:
        from engine.staging_manager import DeckStagingManager
        mgr = DeckStagingManager()
        return mgr.get_archetypes_for_act(session_id=session_id, act=act)
    except Exception as e:
        logger.exception(f"Failed to get archetypes for session {session_id}, act {act}: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def handle_persuaid_stage_act(args: Dict[str, Any]) -> Dict[str, Any]:
    session_id = args["session_id"]
    act = args["act"]
    slides = args["slides"]

    try:
        from engine.staging_manager import DeckStagingManager
        mgr = DeckStagingManager()
        return mgr.stage_act(session_id=session_id, act=act, slides=slides)
    except Exception as e:
        logger.exception(f"Failed to stage act {act} for session {session_id}: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def handle_persuaid_compile_session(args: Dict[str, Any]) -> Dict[str, Any]:
    session_id = args["session_id"]
    out_dir = args.get("out_dir", ".")

    try:
        from engine.universal_compiler import UniversalDeckCompiler
        compiler = UniversalDeckCompiler()
        res = compiler.compile_session(session_id=session_id, out_dir=out_dir)
        if res.get("status") == "success" and res.get("deck_path"):
            dp = Path(res["deck_path"])
            _GENERATED_DECKS[dp.name] = dp
            res["download_url"] = f"/download/{dp.name}"
        return res
    except Exception as e:
        logger.exception(f"Failed to compile session {session_id}: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


TOOL_HANDLERS = {
    "persuaid_start_pipeline": handle_persuaid_start_pipeline,
    "persuaid_get_pipeline_status": handle_persuaid_get_pipeline_status,
    "persuaid_run_pipeline": handle_persuaid_run_pipeline,
    "persuaid_audit_query": handle_persuaid_audit_query,
    "persuaid_format_queries": handle_persuaid_format_queries,
    "persuaid_aggregate_metrics": handle_persuaid_aggregate_metrics,
    "persuaid_configure_credentials": handle_persuaid_configure_credentials,
    "persuaid_generate_deck": handle_persuaid_generate_deck,
    "persuaid_learn_template": handle_persuaid_learn_template,
    "persuaid_init_session": handle_persuaid_init_session,
    "persuaid_get_archetypes": handle_persuaid_get_archetypes,
    "persuaid_stage_act": handle_persuaid_stage_act,
    "persuaid_compile_session": handle_persuaid_compile_session,
}


def process_json_rpc(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Processes incoming JSON-RPC 2.0 requests according to MCP Specification."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if not method:
        return None

    if method == "notifications/initialized":
        logger.info("Client MCP handshake completed.")
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": SERVER_CAPABILITIES,
                "serverInfo": SERVER_INFO,
            },
        }

    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS,
            },
        }

    if method == "resources/list":
        # Scan known locations for PPTX files
        resources = []
        seen = set()
        # 1. Registered decks
        for fname, fpath in _GENERATED_DECKS.items():
            if fpath.exists() and fname not in seen:
                seen.add(fname)
                resources.append({
                    "uri": f"persuaid://decks/{fname}",
                    "name": fname,
                    "description": f"Compiled PowerPoint presentation ({round(fpath.stat().st_size / 1024.0, 1)} KB)",
                    "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                })
        # 2. Check /app/data, /tmp/persuaid_decks, .
        for search_dir in [Path("/app/data"), Path("/tmp/persuaid_decks"), Path(".")]:
            if search_dir.exists():
                for pptx_f in search_dir.glob("*.pptx"):
                    if pptx_f.name not in seen:
                        seen.add(pptx_f.name)
                        _GENERATED_DECKS[pptx_f.name] = pptx_f
                        resources.append({
                            "uri": f"persuaid://decks/{pptx_f.name}",
                            "name": pptx_f.name,
                            "description": f"Compiled PowerPoint presentation ({round(pptx_f.stat().st_size / 1024.0, 1)} KB)",
                            "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        })
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": resources,
            },
        }

    if method == "resources/read":
        uri = params.get("uri", "")
        fname = uri.replace("persuaid://decks/", "").strip()
        fpath = _GENERATED_DECKS.get(fname)
        if not fpath or not fpath.exists():
            # Check fallback locations
            for search_dir in [Path("/app/data"), Path("/tmp/persuaid_decks"), Path(".")]:
                candidate = search_dir / fname
                if candidate.exists():
                    fpath = candidate
                    break

        if not fpath or not fpath.exists():
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Resource not found for URI: {uri}",
                },
            }

        import base64
        blob_b64 = base64.b64encode(fpath.read_bytes()).decode("ascii")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        "blob": blob_b64,
                    }
                ],
            },
        }

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found.",
                },
            }

        try:
            result_data = handler(tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result_data, indent=2, ensure_ascii=False),
                        }
                    ],
                    "isError": result_data.get("status") == "error" or "error" in result_data,
                },
            }
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"status": "error", "error": str(e)}),
                        }
                    ],
                    "isError": True,
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method '{method}' not recognized.",
        },
    }


handle_jsonrpc_request = process_json_rpc


def run_stdio_server():
    logger.info("PersuAId MCP Server v1.4.0 started on stdio.")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line_str = line.strip()
            if not line_str:
                continue

            try:
                request = json.loads(line_str)
            except json.JSONDecodeError as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {e}",
                    },
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
                continue

            response = process_json_rpc(request)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()

        except Exception as e:
            logger.error(f"Stdio server loop error: {e}", exc_info=True)
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal JSON-RPC error: {e}",
                },
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


def main():
    run_stdio_server()


if __name__ == "__main__":
    main()
