#!/usr/bin/env python3
"""
PersuAId Remote MCP (Model Context Protocol) HTTP & SSE Server
Provides production-ready HTTP and Server-Sent Events (SSE) transports for Coolify / Docker hosting.

Endpoints:
- GET  /health, /     : Healthcheck and server capability manifest
- GET  /sse           : Standard MCP Server-Sent Events stream for remote AI agents (Claude Desktop, Cursor, ZCode)
- POST /messages      : Session-scoped message handler for SSE transport
- POST /mcp, /jsonrpc : Direct HTTP JSON-RPC 2.0 endpoint
"""

import asyncio
import http.server
import json
import logging
import os
import sys
import threading
import time
import urllib.parse
import uuid
from pathlib import Path
from queue import Queue, Empty
from typing import Any, Dict, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.mcp_server import (
    handle_jsonrpc_request,
    SERVER_INFO,
    SERVER_CAPABILITIES,
    TOOLS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [persuaid-mcp-http] %(message)s",
)
logger = logging.getLogger("persuaid-mcp-http")

AUTH_TOKEN = os.environ.get("PERSUAID_AUTH_TOKEN", "").strip()


def is_authorized(headers: Dict[str, str], query_params: Dict[str, str]) -> bool:
    """Validates optional bearer token authentication if PERSUAID_AUTH_TOKEN is set."""
    if not AUTH_TOKEN:
        return True
    auth_header = headers.get("authorization", "") or headers.get("Authorization", "")
    token_param = query_params.get("token", "")
    expected = f"Bearer {AUTH_TOKEN}"
    return auth_header == expected or token_param == AUTH_TOKEN


# ==============================================================================
# Standard Library Threading HTTP & SSE Server (Zero external dependencies)
# ==============================================================================

# Active SSE Sessions: {session_id: Queue}
active_sse_queues: Dict[str, Queue] = {}


class PersuAIdHTTPHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        logger.info(f"{self.client_address[0]} - {format % args}")

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = dict(urllib.parse.parse_qsl(parsed.query))

        if not is_authorized(dict(self.headers), params):
            self.send_response(401)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
            return

        if path in ["/health", "/", ""]:
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            resp_body = json.dumps({
                "status": "healthy",
                "service": "persuaid-mcp",
                "version": SERVER_INFO["version"],
                "transports": {
                    "sse": "/sse",
                    "messages": "/messages?session_id=<session_id>",
                    "direct_http": "/mcp",
                },
                "tools_count": len(TOOLS),
            }, indent=2).encode("utf-8")
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)
            return

        elif path == "/sse":
            session_id = uuid.uuid4().hex
            msg_queue = Queue()
            active_sse_queues[session_id] = msg_queue
            logger.info(f"SSE Client connected: session_id={session_id}")

            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            # Emit endpoint event per MCP specification
            host = self.headers.get("Host", "localhost:8000")
            scheme = "https" if self.headers.get("X-Forwarded-Proto") == "https" else "http"
            endpoint_url = f"{scheme}://{host}/messages?session_id={session_id}"
            
            try:
                init_msg = f"event: endpoint\ndata: {endpoint_url}\n\n".encode("utf-8")
                self.wfile.write(init_msg)
                self.wfile.flush()

                while True:
                    try:
                        # Wait for message in queue or send keepalive ping after 15s
                        msg = msg_queue.get(timeout=15.0)
                        event_data = f"event: message\ndata: {json.dumps(msg)}\n\n".encode("utf-8")
                        self.wfile.write(event_data)
                        self.wfile.flush()
                    except Empty:
                        self.wfile.write(b": keep-alive\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                active_sse_queues.pop(session_id, None)
                logger.info(f"SSE Client disconnected: session_id={session_id}")
            return

        else:
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Path '{path}' not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = dict(urllib.parse.parse_qsl(parsed.query))

        if not is_authorized(dict(self.headers), params):
            self.send_response(401)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            payload = json.loads(body)
        except Exception as e:
            self.send_response(400)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}}).encode("utf-8"))
            return

        if path in ["/mcp", "/jsonrpc"]:
            # Direct HTTP JSON-RPC endpoint (synchronous)
            response = handle_jsonrpc_request(payload)
            if response is None:
                self.send_response(204)
                self._send_cors_headers()
                self.end_headers()
                return

            resp_data = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_data)))
            self.end_headers()
            self.wfile.write(resp_data)
            return

        elif path == "/messages":
            session_id = params.get("session_id", "").strip()
            if not session_id or session_id not in active_sse_queues:
                self.send_response(404)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Session '{session_id}' not found or closed."}).encode("utf-8"))
                return

            # Respond immediately with 202 Accepted
            self.send_response(202)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            resp_bytes = json.dumps({"status": "accepted"}).encode("utf-8")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)

            # Process asynchronously in worker thread and push result down the SSE connection
            def async_worker(sess_id: str, rpc_payload: dict):
                try:
                    response = handle_jsonrpc_request(rpc_payload)
                    if response is not None:
                        q = active_sse_queues.get(sess_id)
                        if q:
                            q.put(response)
                except Exception as ex:
                    logger.error(f"Error processing async SSE RPC message: {ex}")

            threading.Thread(target=async_worker, args=(session_id, payload), daemon=True).start()
            return

        else:
            self.send_response(404)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"POST path '{path}' not found"}).encode("utf-8"))


def run_server(host: str = "0.0.0.0", port: int = 8000):
    server = http.server.ThreadingHTTPServer((host, port), PersuAIdHTTPHandler)
    logger.info(f"🚀 PersuAId MCP HTTP/SSE Server listening on http://{host}:{port}")
    logger.info(f"   • Health Check : http://{host}:{port}/health")
    logger.info(f"   • MCP SSE      : http://{host}:{port}/sse")
    logger.info(f"   • Direct MCP   : http://{host}:{port}/mcp")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        server.server_close()


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    run_server(host=host, port=port)


if __name__ == "__main__":
    main()
