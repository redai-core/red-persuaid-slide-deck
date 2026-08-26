import logging
import tempfile
import time
from typing import Callable, List, Optional
from camoufox.sync_api import Camoufox
from src.drivers.base import BaseDriver, LoginWallException
from src.models import AuditResult, Citation

logger = logging.getLogger("actor.gemini")


class GeminiDriver(BaseDriver):
    PLATFORM_NAME = "gemini"
    BASE_URL = "https://gemini.google.com/app"

    def _open_new_chat(self, page) -> None:
        """Navigates to a fresh Gemini chat session."""
        logger.info("Opening a fresh Gemini new chat...")
        new_chat_opened = False
        new_chat_selectors = [
            'a[aria-label="New chat"]',
            'button[aria-label="New chat"]',
            'a[aria-label="Obrolan baru"]',
            'button[aria-label="Obrolan baru"]',
            'a[href="/app"]',
            'a:has-text("New chat")',
            'button:has-text("New chat")',
            'a:has-text("Obrolan baru")',
            'button:has-text("Obrolan baru")',
        ]
        for sel in new_chat_selectors:
            try:
                loc = page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click(timeout=2000)
                    time.sleep(1)
                    new_chat_opened = True
                    break
            except Exception:
                pass

        if not new_chat_opened:
            try:
                page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                time.sleep(1.5)
            except Exception:
                pass

    def _execute_query_on_page(
        self,
        page,
        query: str,
        brand_name: Optional[str] = None,
        brand_domain: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        start_time: Optional[float] = None,
    ) -> AuditResult:
        if start_time is None:
            start_time = time.time()

        input_sel = "rich-textarea, div[contenteditable='true'], textarea, [aria-label*='prompt'], [aria-label*='Ask Gemini'], .ql-editor"
        try:
            logger.info("Locating Gemini input box...")
            input_loc = page.locator(input_sel).locator("visible=true").first
            input_loc.wait_for(state="visible", timeout=15000)
            input_loc.click(force=True, timeout=5000)
        except Exception as e:
            if "accounts.google.com" in page.url.lower() or page.locator("a:has-text('Sign in'), button:has-text('Sign in')").is_visible():
                raise LoginWallException(f"Gemini requires authenticated Google login on {page.url}")
            raise LoginWallException(f"Gemini input prompt not accessible on {page.url}: {e}")

        # Safe text insertion
        logger.info("Typing query into Gemini...")
        try:
            page.keyboard.insert_text(query)
        except Exception:
            page.keyboard.type(query, delay=10)

        time.sleep(0.5)

        # Send prompt
        logger.info("Submitting query...")
        try:
            send_btn = page.locator('button[aria-label*="Send"], button.send-button, [data-testid="send-button"]').locator("visible=true").first
            if send_btn.is_visible():
                send_btn.click()
            else:
                page.keyboard.press("Enter")
        except Exception:
            page.keyboard.press("Enter")

        # Wait for response completion
        logger.info("Waiting for Gemini response stream...")
        time.sleep(8)
        try:
            page.wait_for_selector('button[aria-label*="Stop"]', state="detached", timeout=60000)
        except Exception:
            pass

        logger.info("Streaming finished. Settling markdown DOM...")
        time.sleep(3)

        # Scroll down to ensure full response and citation chips are rendered
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
        except Exception:
            pass

        # Extract response text
        response_sel = ".model-response-text, message-content, [data-test-id='model-response-text']"
        try:
            page.wait_for_selector(response_sel, timeout=15000)
        except Exception as e:
            raise RuntimeError(f"Gemini response not rendered: {e}")

        last_msg = page.locator(response_sel).last
        try:
            last_msg.scroll_into_view_if_needed(timeout=2000)
        except Exception:
            pass
        raw_text = last_msg.inner_text()

        if not raw_text.strip():
            raise RuntimeError("Empty response received from Gemini")

        # Extract citation chips / grounding links
        raw_links: List[str] = page.locator("a[href]").evaluate_all(
            """elements => elements
                .map(el => el.href)
                .filter(href => /^https?:/.test(href) && !href.includes('google.com'))"""
        )
        unique_links = list(dict.fromkeys(raw_links))
        citations = [
            Citation.from_url(link, brand_domain=brand_domain, position=idx)
            for idx, link in enumerate(unique_links, 1)
        ]
        citation_domains = list(dict.fromkeys(c.domain for c in citations))

        duration = time.time() - start_time
        brand_cited = self.check_brand_presence(raw_text, brand_name)
        brand_domain_cited = any(c.is_brand_domain for c in citations)
        competitors_mentioned = self.find_competitor_mentions(raw_text, competitors)

        return AuditResult(
            platform=self.PLATFORM_NAME,
            query=query,
            brand_name=brand_name,
            brand_domain=brand_domain,
            brand_cited=brand_cited,
            brand_domain_cited=brand_domain_cited,
            competitors_mentioned=competitors_mentioned,
            citations=citations,
            citation_domains=citation_domains,
            raw_response_text=raw_text,
            response_length=len(raw_text),
            duration_seconds=round(duration, 2),
        )

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
        """Runs a batch of Gemini queries sequentially inside a warm browser context."""
        results: List[AuditResult] = []
        proxy_dict = self.get_camoufox_proxy_dict()

        with tempfile.TemporaryDirectory() as temp_dir:
            camoufox_kwargs = {
                "headless": False,
                "humanize": True,
                "geoip": True,
                "persistent_context": True,
                "user_data_dir": temp_dir,
            }
            if proxy_dict:
                camoufox_kwargs["proxy"] = proxy_dict

            logger.info(f"Starting warm Camoufox session for {len(queries)} Gemini queries...")
            with Camoufox(**camoufox_kwargs) as context:
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(self.BASE_URL, wait_until="domcontentloaded")
                time.sleep(2)

                # Google Cookie Consent / Welcome Dialogs
                try:
                    consent_btn = page.locator('button:has-text("Accept all"), button:has-text("I agree"), button:has-text("Setuju"), button:has-text("Accept"), button:has-text("Stay logged out"), button:has-text("Try Gemini")')
                    if consent_btn.count() > 0 and consent_btn.first.is_visible():
                        consent_btn.first.click(timeout=3000)
                        time.sleep(1)
                except Exception:
                    pass

                if "accounts.google.com" in page.url.lower():
                    raise LoginWallException("Redirected to Google Accounts login wall")

                for idx, query in enumerate(queries, 1):
                    logger.info(f"[{idx}/{len(queries)}] Executing query on Gemini: '{query}'")
                    q_start_time = time.time()
                    try:
                        if idx > 1:
                            self._open_new_chat(page)
                            if delay_between > 0:
                                time.sleep(delay_between)

                        result = self._execute_query_on_page(
                            page=page,
                            query=query,
                            brand_name=brand_name,
                            brand_domain=brand_domain,
                            competitors=competitors,
                            start_time=q_start_time,
                        )
                    except Exception as e:
                        logger.error(f"[{idx}/{len(queries)}] Gemini query failed: {e}")
                        result = AuditResult(
                            platform=self.PLATFORM_NAME,
                            query=query,
                            brand_name=brand_name,
                            brand_domain=brand_domain,
                            error=str(e),
                            duration_seconds=round(time.time() - q_start_time, 2),
                        )

                    results.append(result)
                    if on_result:
                        try:
                            on_result(result)
                        except Exception as cb_err:
                            logger.warning(f"on_result callback warning: {cb_err}")

        return results

    def run_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        brand_domain: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        session_cookies: Optional[str] = None,
    ) -> AuditResult:
        results = self.run_batch(
            queries=[query],
            brand_name=brand_name,
            brand_domain=brand_domain,
            competitors=competitors,
            session_cookies=session_cookies,
        )
        if results:
            return results[0]
        raise RuntimeError(f"Failed to execute Gemini query '{query}'")
