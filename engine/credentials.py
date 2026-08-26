#!/usr/bin/env python3
"""
PersuAId Secure Local Credential Manager
Safely stores and retrieves credentials (such as Apify API tokens) in the user's home
directory (~/.persuaid/credentials.json) with restricted file permissions (0600 / rw-------).
"""

import json
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".persuaid"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"


def get_stored_token(key: str = "apify_token") -> Optional[str]:
    """Reads a stored credential from ~/.persuaid/credentials.json if available."""
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        val = data.get(key)
        return val.strip() if isinstance(val, str) and val.strip() else None
    except Exception:
        return None


def store_token(token: str, key: str = "apify_token") -> str:
    """
    Saves a credential to ~/.persuaid/credentials.json with 0600 (owner-only) permissions.
    Creates directory ~/.persuaid with 0700 permissions if it doesn't exist.
    """
    clean_token = token.strip()
    if not clean_token:
        raise ValueError("Cannot store empty token.")

    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Enforce directory permissions
    try:
        os.chmod(CONFIG_DIR, 0o700)
    except Exception:
        pass

    data = {}
    if CREDENTIALS_FILE.exists():
        try:
            data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    data[key] = clean_token
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Enforce file permissions: Read/Write by owner ONLY (0600)
    try:
        os.chmod(CREDENTIALS_FILE, 0o600)
    except Exception:
        pass

    return clean_token


def resolve_apify_token(override: Optional[str] = None) -> Optional[str]:
    """
    Resolves the active Apify API token in priority order:
    1. Direct override (e.g. from CLI --apify-token) -> automatically persists locally
    2. APIFY_TOKEN environment variable
    3. Stored token in ~/.persuaid/credentials.json
    Returns None if no token is configured.
    """
    if override and override.strip():
        token = override.strip()
        try:
            store_token(token)
        except Exception:
            pass
        return token

    env_token = os.environ.get("APIFY_TOKEN")
    if env_token and env_token.strip():
        return env_token.strip()

    return get_stored_token("apify_token")


def has_apify_token() -> bool:
    """Returns True if an Apify token is available in environment or local config."""
    return resolve_apify_token() is not None
