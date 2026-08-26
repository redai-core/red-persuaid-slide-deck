import asyncio
import logging
import sys
import time
from collections import Counter
from typing import Any, Dict, List

from apify import Actor
from src.drivers.chatgpt import ChatGPTDriver
from src.drivers.gemini import GeminiDriver
from src.models import ActorInput, AuditResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("actor")


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        logger.info(f"Received Actor Input: {actor_input}")

        # Validate input with Pydantic
        try:
            validated_input = ActorInput(**actor_input)
        except Exception as e:
            logger.error(f"Invalid input schema: {e}")
            await Actor.fail(status_message=f"Invalid input: {e}")
            return

        queries: List[str] = [q.strip() for q in validated_input.queries if q and q.strip()]
        if not queries:
            logger.error("No valid queries provided.")
            await Actor.fail(status_message="Empty queries list provided.")
            return

        platform: str = validated_input.platform.lower()
        brand_name: str = validated_input.brand_name or ""
        brand_domain: str = validated_input.brand_domain or ""
        competitors: List[str] = validated_input.competitors
        delay: int = validated_input.delayBetweenQueries
        session_cookies: str = validated_input.sessionCookies or ""

        # Initialize Apify Proxy Configuration (default to Residential proxy for stealth)
        proxy_url: str = ""
        proxy_input = validated_input.proxyConfiguration
        if proxy_input is None:
            proxy_input = {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}

        try:
            proxy_config = await Actor.create_proxy_configuration(actor_proxy_input=proxy_input)
            if proxy_config:
                proxy_url = await proxy_config.new_url() or ""
                logger.info("Initialized Apify Proxy configuration successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize Apify proxy: {e}. Falling back to direct connection.")

        # Instantiate Camoufox driver
        if platform == "gemini":
            driver = GeminiDriver(proxy_url=proxy_url)
        else:
            driver = ChatGPTDriver(proxy_url=proxy_url)

        logger.info(f"Starting batched audit for {len(queries)} queries on {platform.upper()} (Brand: '{brand_name}', Domain: '{brand_domain}')")

        results: List[AuditResult] = []
        all_citation_domains: List[str] = []
        brand_presence_count = 0
        brand_domain_citation_count = 0
        competitor_mention_counts: Counter = Counter()

        loop = asyncio.get_running_loop()

        def on_query_completed(result: AuditResult) -> None:
            nonlocal brand_presence_count, brand_domain_citation_count
            dataset_item = result.to_dataset_item()
            # Push live output to default Apify dataset thread-safely
            asyncio.run_coroutine_threadsafe(Actor.push_data(dataset_item), loop)

            if result.brand_cited:
                brand_presence_count += 1
            if result.brand_domain_cited:
                brand_domain_citation_count += 1
            for comp in result.competitors_mentioned:
                competitor_mention_counts[comp] += 1
            all_citation_domains.extend(result.citation_domains)

            logger.info(
                f"Completed query on warm session: Brand cited: {result.brand_cited} | Citations: {len(result.citations)} | Text length: {len(result.raw_response_text)} | Duration: {result.duration_seconds}s"
            )

        # Run entire batch in 1 warm browser instance with new chat navigation
        results = await asyncio.to_thread(
            driver.run_batch,
            queries=queries,
            brand_name=brand_name if brand_name else None,
            brand_domain=brand_domain if brand_domain else None,
            competitors=competitors,
            session_cookies=session_cookies if session_cookies else None,
            delay_between=delay,
            on_result=on_query_completed,
        )

        # Compute summary metrics
        total_queries = len(queries)
        presence_rate = round((brand_presence_count / total_queries) * 100, 1) if total_queries > 0 else 0.0
        domain_citation_rate = round((brand_domain_citation_count / total_queries) * 100, 1) if total_queries > 0 else 0.0

        top_sources = [
            {"domain": dom, "citations": count}
            for dom, count in Counter(all_citation_domains).most_common(10)
        ]

        summary: Dict[str, Any] = {
            "platform": platform,
            "brand_name": brand_name,
            "brand_domain": brand_domain,
            "total_queries_audited": total_queries,
            "brand_presence_count": brand_presence_count,
            "brand_presence_rate_pct": presence_rate,
            "brand_domain_citation_count": brand_domain_citation_count,
            "brand_domain_citation_rate_pct": domain_citation_rate,
            "competitor_mentions": dict(competitor_mention_counts),
            "top_citation_sources": top_sources,
            "successful_audits": sum(1 for r in results if not r.error and len(r.raw_response_text) > 0),
            "failed_audits": sum(1 for r in results if r.error or len(r.raw_response_text) == 0),
        }

        logger.info(f"Audit Complete! Summary: {summary}")
        # Save final summary to Key-Value Store
        await Actor.set_value("OUTPUT", summary)


if __name__ == "__main__":
    asyncio.run(main())
