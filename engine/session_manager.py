from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta, timezone
from engine.models import AccountInfo


class SessionManager:
    def __init__(self, base_dir: Path | str = "profiles"):
        self.base_dir = Path(base_dir)
        self.cooldown_registry: Dict[str, AccountInfo] = {}

    def get_chatgpt_storage_path(self, account_name: str) -> Path:
        p = self.base_dir / "chatgpt" / f"{account_name}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def get_gemini_profile_dir(self, account_name: str) -> Path:
        p = self.base_dir / "gemini" / f"{account_name}_profile"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def list_accounts(self, platform: str) -> List[str]:
        target_dir = self.base_dir / platform
        if not target_dir.exists():
            return []
        if platform == "chatgpt":
            return [f.stem for f in target_dir.glob("*.json")]
        elif platform == "gemini":
            return [d.name.replace("_profile", "") for d in target_dir.iterdir() if d.is_dir()]
        return []

    def get_next_available_account(self, platform: str) -> Optional[str]:
        accounts = self.list_accounts(platform)
        if not accounts:
            return None
        for acc in accounts:
            key = f"{platform}:{acc}"
            info = self.cooldown_registry.get(key)
            if not info or info.is_available():
                return acc
        return None

    def mark_rate_limited(self, platform: str, account_name: str, cooldown_minutes: int = 60) -> None:
        key = f"{platform}:{account_name}"
        until = datetime.now(timezone.utc) + timedelta(minutes=cooldown_minutes)
        self.cooldown_registry[key] = AccountInfo(
            platform=platform,
            account_name=account_name,
            is_rate_limited=True,
            rate_limited_until=until
        )
