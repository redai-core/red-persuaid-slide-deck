import json
import logging
import re
import time
from typing import Callable, List, Optional
from urllib.parse import urlparse
from camoufox.sync_api import Camoufox
from src.drivers.base import BaseDriver, LoginWallException
from src.models import AuditResult, Citation

logger = logging.getLogger("actor.chatgpt")


class ChatGPTDriver(BaseDriver):
    PLATFORM_NAME = "chatgpt"
    BASE_URL = "https://chatgpt.com"

    def _dismiss_overlays(self, page) -> None:
        """Dismisses common guest modals, cookie banners, and onboarding overlays."""
        dismiss_selectors = [
            'button:has-text("Stay logged out")',
            'button:has-text("Tetap keluar")',
            'button:has-text("Try it first")',
            'button:has-text("Dismiss")',
            'button:has-text("Tutup")',
            'button:has-text("Close")',
            'button:has-text("Got it")',
            'button:has-text("Mengerti")',
            'button:has-text("Accept all")',
            'button:has-text("Agree")',
            'button:has-text("Setuju")',
            'button:has-text("Next")',
            'button:has-text("Lanjut")',
            'button[aria-label="Close"]',
            'button[aria-label="Tutup"]',
            '[role="dialog"] button:has-text("Stay logged out")',
            '[role="dialog"] button:has-text("Tetap keluar")',
            '[role="dialog"] button:has-text("Dismiss")',
            '[role="dialog"] button:has-text("Close")',
        ]
        for sel in dismiss_selectors:
            try:
                btn = page.locator(sel)
                if btn.count() > 0 and btn.first.is_visible():
                    logger.info(f"Dismissing overlay: {sel}")
                    btn.first.click(timeout=1500)
                    time.sleep(0.5)
            except Exception:
                pass

    def _wait_for_turnstile_if_present(self, page, max_wait_seconds: int = 20) -> None:
        """Allows Camoufox stealth solver to resolve Cloudflare Turnstile if present."""
        turnstile_loc = page.locator('iframe[src*="cloudflare"], iframe[src*="turnstile"], iframe[title*="Cloudflare"], iframe[title*="Turnstile"], div#turnstile-wrapper')
        start = time.time()
        while time.time() - start < max_wait_seconds:
            try:
                if turnstile_loc.count() > 0 and turnstile_loc.first.is_visible():
                    logger.info("Cloudflare Turnstile challenge detected. Allowing solver to resolve...")
                    time.sleep(2)
                else:
                    break
            except Exception:
                break

    def _open_new_chat(self, page) -> None:
        """Navigates to a fresh, clean chat session on ChatGPT without restarting the browser."""
        logger.info("Opening a fresh new chat session...")
        new_chat_opened = False

        # 1. Try clicking 'New chat' button in sidebar/topbar
        new_chat_selectors = [
            '[data-testid="create-new-chat-button"]',
            'a[aria-label="New chat"]',
            'button[aria-label="New chat"]',
            'a[aria-label="Obrolan baru"]',
            'button[aria-label="Obrolan baru"]',
            'a[href="/"]',
            'a[href="https://chatgpt.com/"]',
            'a:has-text("New chat")',
            'button:has-text("New chat")',
            'a:has-text("Obrolan baru")',
            'button:has-text("Obrolan baru")',
            'button[aria-label*="New"]',
            'a[aria-label*="New"]',
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

        # 2. Try keyboard shortcut Ctrl+Shift+O if button was not found
        if not new_chat_opened:
            try:
                page.keyboard.press("Control+Shift+o")
                time.sleep(1)
                if page.url.rstrip("/").endswith("chatgpt.com"):
                    new_chat_opened = True
            except Exception:
                pass

        # 3. Fallback: navigate directly to base URL
        if not new_chat_opened or not page.url.rstrip("/").endswith("chatgpt.com"):
            try:
                page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                time.sleep(1.5)
            except Exception as e:
                logger.warning(f"Direct navigation to {self.BASE_URL} encountered: {e}")

        # 4. Settle DOM, dismiss any popup overlays
        self._dismiss_overlays(page)

        # 5. Wait for input textarea to become available
        input_sel = (
            page.locator("#prompt-textarea")
            .or_(page.locator("div#prompt-textarea"))
            .or_(page.locator("textarea[placeholder*='Ask']"))
            .or_(page.locator("textarea[placeholder*='Tanya']"))
            .or_(page.locator("div[contenteditable='true']"))
            .or_(page.locator("#mobile-composer-prompt"))
        ).locator("visible=true").first

        try:
            input_sel.wait_for(state="visible", timeout=15000)
            logger.info("New chat ready for next prompt.")
        except Exception:
            self._dismiss_overlays(page)
            input_sel.wait_for(state="visible", timeout=10000)

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

        # Locate active visible input box
        logger.info("Locating ChatGPT input box...")
        composer_selectors = [
            "#prompt-textarea",
            "div#prompt-textarea",
            "textarea[placeholder*='Ask']",
            "textarea[placeholder*='Tanya']",
            "textarea[placeholder*='Message']",
            "div[contenteditable='true']",
            "#mobile-composer-prompt",
        ]
        
        input_loc = None
        for sel in composer_selectors:
            loc = page.locator(sel).locator("visible=true")
            if loc.count() > 0:
                input_loc = loc.first
                break

        if input_loc is None:
            combined_loc = (
                page.locator("#prompt-textarea")
                .or_(page.locator("textarea[placeholder*='Ask']"))
                .or_(page.locator("textarea[placeholder*='Tanya']"))
                .or_(page.locator("div[contenteditable='true']"))
                .or_(page.locator("#mobile-composer-prompt"))
            ).locator("visible=true").first
            try:
                combined_loc.wait_for(state="visible", timeout=20000)
                input_loc = combined_loc
            except Exception:
                self._dismiss_overlays(page)
                combined_loc.wait_for(state="visible", timeout=10000)
                input_loc = combined_loc

        # Focus and enter text into prompt box
        logger.info("Typing query into prompt box...")
        try:
            input_loc.click(force=True, timeout=5000)
        except Exception:
            try:
                input_loc.focus(timeout=3000)
            except Exception:
                pass

        time.sleep(0.3)
        try:
            page.keyboard.insert_text(query)
        except Exception:
            try:
                input_loc.fill(query)
            except Exception:
                page.keyboard.type(query, delay=10)

        time.sleep(0.5)

        # Submit query
        logger.info("Submitting query...")
        submitted = False
        try:
            send_btn = (
                page.locator('button[data-testid="send-button"]')
                .or_(page.locator('button[aria-label*="Send"]'))
                .or_(page.locator('button[aria-label*="Kirim"]'))
                .or_(page.locator('button.wm-composer-sendButton'))
                .or_(page.locator('button[type="submit"]'))
            ).locator("visible=true").first
            if send_btn.count() > 0 and send_btn.is_visible():
                send_btn.click(force=True, timeout=3000)
                submitted = True
        except Exception:
            pass

        if not submitted:
            page.keyboard.press("Enter")

        # Monitor streaming completion with fast polling
        logger.info("Monitoring AI response stream...")
        last_len = 0
        stable_count = 0
        for i in range(45):
            time.sleep(1.5)
            stop_btn = page.locator('button[data-testid="stop-button"], button[aria-label*="Stop"], button[aria-label*="Berhenti"]')
            is_generating = (stop_btn.count() > 0 and stop_btn.first.is_visible())

            current_text = page.evaluate("""() => {
                const turns = document.querySelectorAll('[data-message-author-role="assistant"]');
                if (turns.length > 0) {
                    return turns[turns.length - 1].innerText || '';
                }
                const articles = document.querySelectorAll('article');
                if (articles.length > 0) {
                    return articles[articles.length - 1].innerText || '';
                }
                const mds = document.querySelectorAll('main .markdown, main .prose');
                if (mds.length > 0) {
                    return mds[mds.length - 1].innerText || '';
                }
                return '';
            }""").strip()

            cur_len = len(current_text)
            # Once we have text (>20 chars) and generation stops or text length stops growing
            if cur_len > 20 and cur_len == last_len and not is_generating:
                stable_count += 1
                if stable_count >= 2:
                    logger.info(f"Stream completed smoothly in ~{(i+1)*1.5:.1f}s ({cur_len} chars).")
                    break
            else:
                stable_count = 0
                last_len = cur_len

        logger.info("Streaming finished. Settling markdown DOM...")
        time.sleep(1)

        # Scroll down to ensure full message DOM and citation chips are rendered
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
        except Exception:
            pass

        # Extract main assistant response text cleanly
        raw_text = page.evaluate("""() => {
            const assistantTurns = document.querySelectorAll('[data-message-author-role="assistant"]');
            for (let i = assistantTurns.length - 1; i >= 0; i--) {
                const md = assistantTurns[i].querySelector('.markdown, .prose, [class*="markdown"]') || assistantTurns[i];
                const txt = (md.innerText || '').trim();
                if (txt.length > 20) return txt;
            }

            const mainMds = document.querySelectorAll('main .markdown, main [class*="markdown"], main .prose');
            if (mainMds.length > 0) {
                const txt = (mainMds[mainMds.length - 1].innerText || '').trim();
                if (txt.length > 20) return txt;
            }

            const mainEl = document.querySelector('main');
            const fullText = (mainEl ? mainEl.innerText : document.body.innerText) || '';
            const splitRegex = /(?:ChatGPT\s*(?:said|bilang|berkata|dijo|சொன்னது|dit|hat gesagt)?\s*:\s*)([\s\S]*)/i;
            const match = fullText.match(splitRegex);
            if (match && match[1] && match[1].trim().length > 20) {
                return match[1].trim();
            }

            return '';
        }""").strip()

        if not raw_text or len(raw_text) < 20:
            raise RuntimeError("Empty or invalid response received from ChatGPT")

        # Try to expand "Sources" button to populate citation links
        try:
            source_buttons = page.locator('button:has-text("Searched"), button:has-text("Ditelusuri"), button:has-text("Sources"), button:has-text("Sumber"), button[aria-label*="Sources"]')
            if source_buttons.count() > 0 and source_buttons.first.is_visible():
                source_buttons.first.click(timeout=1500)
                time.sleep(0.5)
        except Exception:
            pass

        # Extract external links
        raw_links: List[str] = page.evaluate(
            """() => {
                const links = Array.from(document.querySelectorAll('a[href], [data-citation-url], [data-url], [data-testid*="citation"] a, [data-testid*="attribution"] a, button[data-url], div.markdown a'))
                    .map(el => el.href || el.getAttribute('data-citation-url') || el.getAttribute('data-url') || el.getAttribute('href'))
                    .filter(href => href && /^https?:/i.test(href) && !href.includes('chatgpt.com') && !href.includes('openai.com') && !href.includes('auth0.com'));
                return Array.from(new Set(links));
            }"""
        )
        
        # Regex parse explicit URLs in markdown
        text_urls = re.findall(r'https?://[^\s)\]">]+', raw_text)
        for u in text_urls:
            clean_u = u.rstrip('.,;:')
            if clean_u not in raw_links and not any(k in clean_u.lower() for k in ["chatgpt.com", "openai.com"]):
                raw_links.append(clean_u)

        # Domain mentions in text
        domain_patterns = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+(?:com|id|org|net|io|co|gov|edu|ai|app)\b', raw_text, re.IGNORECASE)
        for d in domain_patterns:
            d_low = d.lower()
            if not any(k in d_low for k in ["chatgpt.com", "openai.com", "google.com", "f-droid.org"]) and not any(d_low in l for l in raw_links):
                raw_links.append(f"https://{d_low}")

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
        """Runs an entire batch of queries sequentially inside a single warm browser session."""
        results: List[AuditResult] = []
        proxy_dict = self.get_camoufox_proxy_dict()

        camoufox_kwargs = {
            "headless": False,
            "humanize": True,
            "geoip": False,
        }
        if proxy_dict:
            camoufox_kwargs["proxy"] = proxy_dict

        storage_state = None
        if session_cookies:
            try:
                storage_state = json.loads(session_cookies)
            except Exception:
                pass

        context_kwargs = {
            "viewport": {"width": 1920, "height": 1080},
            "locale": "id-ID",
            "extra_http_headers": {
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        }
        if storage_state:
            context_kwargs["storage_state"] = storage_state

        logger.info(f"Starting warm Camoufox session for {len(queries)} ChatGPT queries...")
        with Camoufox(**camoufox_kwargs) as browser:
            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            # First query initial warm-up
            logger.info(f"Initial warm-up: Navigating to {self.BASE_URL}...")
            page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=45000)
            time.sleep(2)
            self._wait_for_turnstile_if_present(page)
            self._dismiss_overlays(page)

            # Check for mandatory login wall redirect
            current_url = page.url.lower()
            if "login" in current_url or "auth0" in current_url or "auth/login" in current_url:
                raise LoginWallException(f"Mandatory login wall encountered on {current_url}")

            for idx, query in enumerate(queries, 1):
                logger.info(f"[{idx}/{len(queries)}] Executing query on warm ChatGPT session: '{query}'")
                q_start_time = time.time()
                try:
                    if idx > 1:
                        # Open a fresh new chat for queries 2..N
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
                    logger.error(f"[{idx}/{len(queries)}] Error auditing query '{query}': {e}")
                    result = AuditResult(
                        platform=self.PLATFORM_NAME,
                        query=query,
                        brand_name=brand_name,
                        brand_domain=brand_domain,
                        error=str(e),
                        duration_seconds=round(time.time() - q_start_time, 2),
                    )
                    # Attempt recovery to fresh page/chat for next query in batch
                    try:
                        page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(2)
                        self._dismiss_overlays(page)
                    except Exception:
                        try:
                            page.close()
                            page = context.new_page()
                            page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                            time.sleep(2)
                            self._dismiss_overlays(page)
                        except Exception:
                            pass

                results.append(result)
                if on_result:
                    try:
                        on_result(result)
                    except Exception as cb_err:
                        logger.warning(f"on_result callback warning: {cb_err}")

            try:
                page.close()
            except Exception:
                pass
            try:
                context.close()
            except Exception:
                pass

        return results

    def run_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        brand_domain: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        session_cookies: Optional[str] = None,
        max_retries: int = 1,
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
        raise RuntimeError(f"Failed to execute query '{query}'")
