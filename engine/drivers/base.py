from abc import ABC, abstractmethod
from typing import Optional
import re
from engine.models import AuditResult
from engine.session_manager import SessionManager


class LoginWallException(Exception):
    """Raised when an unauthenticated session is blocked by a mandatory login modal or gate."""
    pass


class BaseDriver(ABC):
    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.session_manager = session_manager or SessionManager()

    @abstractmethod
    def authenticate(self, account_name: str) -> None:
        """Launches headed browser for interactive user login and captures credentials."""
        pass

    @abstractmethod
    def run_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        account_name: Optional[str] = None,
        headless: bool = True,
    ) -> AuditResult:
        """Executes query headlessly, waits for stream completion, and extracts citations."""
        pass

    def check_brand_presence(self, text: Optional[str], brand_name: Optional[str]) -> bool:
        if not brand_name or not text:
            return False
        pattern = rf"\b{re.escape(brand_name)}\b"
        return bool(re.search(pattern, text, re.IGNORECASE))
