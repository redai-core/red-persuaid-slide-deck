#!/usr/bin/env python3
"""
Deploys local actor source files to Apify Actor (calming_monument/ai-search-citation-scraper)
and triggers a new build.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.apify_client import ApifyClient

ACTOR_ID = "7Q9VrTHAcz9koe4Qa"
ACTOR_NAME = "calming_monument/ai-search-citation-scraper"
VERSION_NUMBER = "1.0"
ACTOR_DIR = Path(__file__).resolve().parent


def collect_source_files() -> List[Dict[str, str]]:
    source_files = []
    for root, _, files in os.walk(ACTOR_DIR):
        for f in files:
            file_path = Path(root) / f
            rel_path = file_path.relative_to(ACTOR_DIR).as_posix()
            
            # Skip python caches, deployment scripts, git, and build artifacts
            if any(part.startswith(".") and part != ".actor" for part in Path(rel_path).parts):
                continue
            if "__pycache__" in rel_path or rel_path.endswith(".pyc") or rel_path == "deploy.py":
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                source_files.append({
                    "name": rel_path,
                    "format": "TEXT",
                    "content": content,
                })
            except Exception as e:
                print(f"⚠️ Skipping {rel_path}: {e}")

    return sorted(source_files, key=lambda x: x["name"])


def deploy_and_build():
    print(f"🚀 Deploying source files to Apify Actor '{ACTOR_NAME}' (Version {VERSION_NUMBER})...")
    client = ApifyClient()
    source_files = collect_source_files()
    
    print(f"📦 Collected {len(source_files)} source files:")
    for sf in source_files:
        print(f"   • {sf['name']} ({len(sf['content'])} chars)")

    # 1. Update version source files
    version_payload = {
        "versionNumber": VERSION_NUMBER,
        "sourceType": "SOURCE_FILES",
        "sourceFiles": source_files,
    }
    
    update_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/versions/{VERSION_NUMBER}"
    print(f"\n📡 Updating Actor version on Apify...")
    client._http_request(update_url, method="PUT", data=version_payload)
    print("✓ Version source files updated successfully!")

    # 2. Trigger Build
    build_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/builds?version={VERSION_NUMBER}"
    print(f"\n🔨 Triggering new build on Apify...")
    build_res = client._http_request(build_url, method="POST", data={})
    build_data = build_res.get("data", {})
    build_id = build_data.get("id")
    build_num = build_data.get("buildNumber")
    print(f"✓ Build started: Build #{build_num} (ID: {build_id})")

    # 3. Poll Build Status
    status_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/builds/{build_id}"
    print("⏳ Waiting for build to finish...")
    start_poll = time.time()
    while time.time() - start_poll < 300:
        time.sleep(5)
        status_res = client._http_request(status_url, method="GET")
        data = status_res.get("data", {})
        status = data.get("status")
        print(f"   Status: {status} (elapsed: {int(time.time() - start_poll)}s)")
        if status == "SUCCEEDED":
            print(f"\n🎉 Build #{build_num} SUCCEEDED in {int(time.time() - start_poll)}s!")
            return True
        elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            print(f"\n❌ Build failed with status: {status}")
            return False

    print("⚠️ Build polling timed out after 300s.")
    return False


if __name__ == "__main__":
    success = deploy_and_build()
    sys.exit(0 if success else 1)
