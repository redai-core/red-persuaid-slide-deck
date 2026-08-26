from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field


class Citation(BaseModel):
    url: str
    domain: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    position: Optional[int] = None
    is_brand_domain: bool = False

    @classmethod
    def from_url(cls, url: str, brand_domain: Optional[str] = None, position: Optional[int] = None) -> "Citation":
        clean_url = url.strip()
        parsed = urlparse(clean_url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        is_brand = False
        if brand_domain:
            clean_brand_domain = brand_domain.lower().replace("www.", "").strip()
            is_brand = (domain == clean_brand_domain) or domain.endswith("." + clean_brand_domain)

        return cls(
            url=clean_url,
            domain=domain,
            position=position,
            is_brand_domain=is_brand,
        )


class AuditResult(BaseModel):
    platform: str
    query: str
    brand_name: Optional[str] = None
    brand_domain: Optional[str] = None
    brand_cited: bool = False
    brand_domain_cited: bool = False
    competitors_mentioned: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    citation_domains: List[str] = Field(default_factory=list)
    raw_response_text: str = ""
    response_length: int = 0
    duration_seconds: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: Optional[str] = None

    def to_dataset_item(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "query": self.query,
            "brand_name": self.brand_name,
            "brand_domain": self.brand_domain,
            "brand_cited": self.brand_cited,
            "brand_domain_cited": self.brand_domain_cited,
            "competitors_mentioned": self.competitors_mentioned,
            "citations": [c.model_dump() for c in self.citations],
            "citation_domains": self.citation_domains,
            "raw_response_text": self.raw_response_text,
            "response_length": self.response_length,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
            "error": self.error,
        }


class ActorInput(BaseModel):
    queries: List[str]
    platform: str = "chatgpt"
    brand_name: Optional[str] = None
    brand_domain: Optional[str] = None
    competitors: List[str] = Field(default_factory=list)
    proxyConfiguration: Optional[Dict[str, Any]] = None
    sessionCookies: Optional[str] = None
    delayBetweenQueries: int = 1
