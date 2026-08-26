#!/usr/bin/env python3
"""
PersuAId Data Models
Supports both Pydantic (if installed) and Standard Library dataclasses (if zero-dependency mode).
"""

from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse

try:
    from pydantic import BaseModel, Field

    class Citation(BaseModel):
        url: str
        domain: str
        title: Optional[str] = None

        @classmethod
        def from_url(cls, url: str, title: Optional[str] = None) -> "Citation":
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return cls(url=url, domain=domain, title=title)

    class AuditResult(BaseModel):
        platform: str
        account_id: str
        query: str
        brand_name: Optional[str] = None
        brand_cited: bool = False
        citations: List[Citation] = Field(default_factory=list)
        raw_response_text: str
        response_length: int
        duration_seconds: float
        timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class AccountInfo(BaseModel):
        platform: str
        account_name: str
        is_rate_limited: bool = False
        rate_limited_until: Optional[datetime] = None

        def is_available(self) -> bool:
            if not self.is_rate_limited:
                return True
            if self.rate_limited_until and datetime.now(timezone.utc) > self.rate_limited_until:
                return True
            return False

except ImportError:
    from dataclasses import dataclass, field, asdict

    @dataclass
    class Citation:
        url: str
        domain: str
        title: Optional[str] = None

        @classmethod
        def from_url(cls, url: str, title: Optional[str] = None) -> "Citation":
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return cls(url=url, domain=domain, title=title)

        def model_dump(self, mode: str = "json") -> dict:
            return asdict(self)

    @dataclass
    class AuditResult:
        platform: str
        account_id: str
        query: str
        raw_response_text: str
        response_length: int
        duration_seconds: float
        brand_name: Optional[str] = None
        brand_cited: bool = False
        citations: List[Citation] = field(default_factory=list)
        timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

        def model_dump(self, mode: str = "json") -> dict:
            d = asdict(self)
            if isinstance(d.get("timestamp"), datetime):
                d["timestamp"] = d["timestamp"].isoformat()
            return d

    @dataclass
    class AccountInfo:
        platform: str
        account_name: str
        is_rate_limited: bool = False
        rate_limited_until: Optional[datetime] = None

        def is_available(self) -> bool:
            if not self.is_rate_limited:
                return True
            if self.rate_limited_until and datetime.now(timezone.utc) > self.rate_limited_until:
                return True
            return False
