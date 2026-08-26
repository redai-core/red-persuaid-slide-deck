from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional
import re
from urllib.parse import urlparse
from src.models import AuditResult, Citation


class LoginWallException(Exception):
    """Raised when an unauthenticated session is blocked by a mandatory login modal or gate."""
    pass


class BaseDriver(ABC):
    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url

    def get_camoufox_proxy_dict(self) -> Optional[Dict[str, str]]:
        if not self.proxy_url:
            return None
        
        parsed = urlparse(self.proxy_url)
        server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}" if parsed.port else f"{parsed.scheme}://{parsed.hostname}"
        proxy_dict = {"server": server}
        if parsed.username:
            proxy_dict["username"] = parsed.username
        if parsed.password:
            proxy_dict["password"] = parsed.password
        return proxy_dict

    @abstractmethod
    def run_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        brand_domain: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        session_cookies: Optional[str] = None,
    ) -> AuditResult:
        """Executes query headlessly, waits for stream completion, and extracts citations."""
        pass

    @abstractmethod
    def run_batch(
        self,
        queries: List[str],
        brand_name: Optional[str] = None,
        brand_domain: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        session_cookies: Optional[str] = None,
        delay_between: int = 1,
        on_result: Optional[Callable[[AuditResult], None]] = None,
    ) -> List[AuditResult]:
        """Executes a batch of queries sequentially within a single warm browser instance, starting a new chat per query."""
        pass

    def check_brand_presence(self, text: Optional[str], brand_name: Optional[str]) -> bool:
        if not brand_name or not text:
            return False
        pattern = rf"\b{re.escape(brand_name)}\b"
        return bool(re.search(pattern, text, re.IGNORECASE))

    def find_competitor_mentions(self, text: Optional[str], competitors: Optional[List[str]]) -> List[str]:
        if not competitors or not text:
            return []
        mentioned = []
        for comp in competitors:
            if comp and comp.strip():
                pattern = rf"\b{re.escape(comp.strip())}\b"
                if re.search(pattern, text, re.IGNORECASE):
                    mentioned.append(comp.strip())
        return mentioned
