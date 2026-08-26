import json
import logging
import re
import time
from typing import Callable, List, Optional
from urllib.parse import urlparse
from camoufox.sync_api import Camoufox
from engine.drivers.base import BaseDriver, LoginWallException
from engine.models import AuditResult, Citation
from engine.session_manager import SessionManager

logger = logging.getLogger("engine.drivers.chatgpt")


class ChatGPTDriver(BaseDriver):
    PLATFORM_NAME = "chatgpt"
    BASE_URL = "https://chatgpt.com"

    def authenticate(self, account_name: str) -> None:
        storage_path = self.session_manager.get_chatgpt_storage_path(account_name)
        with Camoufox(headless=False, humanize=True) as browser:
            context = browser.new_context()
            page = context.new_page()
            page.goto(f"{self.BASE_URL}/login")

            # If it lands on the guest prompt page instead of login form, click "Log in"
            time.sleep(2)
            login_btn = page.locator("button:has-text('Log in'), a[href*='login'], [data-testid='login-button']")
            if login_btn.count() > 0 and login_btn.first.is_visible():
                try:
                    login_btn.first.click()
                except Exception:
                    pass

            # Wait until actual session token is present in cookies
            max_wait = 300  # 5 minutes
            start = time.time()
            logged_in = False

            while time.time() - start < max_wait:
                cookies = context.cookies()
                has_auth_token = any(
                    "session-token" in c.get("name", "").lower() or c.get("name") == "__Secure-next-auth.session-token"
                    for c in cookies
                )
                has_profile_menu = (
                    page.locator("[data-testid='user-profile-menu'], [data-testid='profile-button']").count() > 0
                )

                if has_auth_token or has_profile_menu:
                    logged_in = True
                    break
                time.sleep(1)

            if not logged_in:
                raise TimeoutError("Login timed out. No active session token detected within 5 minutes.")

            time.sleep(2)
            context.storage_state(path=str(storage_path))

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
                    btn.first.click(timeout=1500)
                    time.sleep(0.5)
            except Exception:
                pass

    def _open_new_chat(self, page) -> None:
        """Navigates to a fresh, clean chat session on ChatGPT."""
        new_chat_opened = False
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
                page.keyboard.press("Control+Shift+o")
                time.sleep(1)
                if page.url.rstrip("/").endswith("chatgpt.com"):
                    new_chat_opened = True
            except Exception:
                pass

        if not new_chat_opened or not page.url.rstrip("/").endswith("chatgpt.com"):
            try:
                page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                time.sleep(1.5)
            except Exception:
                pass

        self._dismiss_overlays(page)

    def _execute_query_on_page(
        self,
        page,
        query: str,
        brand_name: Optional[str] = None,
        brand_domain: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        account_id: str = "guest",
        start_time: Optional[float] = None,
    ) -> AuditResult:
        if start_time is None:
            start_time = time.time()

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
                combined_loc.wait_for(state="visible", timeout=15000)
                input_loc = combined_loc
            except Exception:
                self._dismiss_overlays(page)
                combined_loc.wait_for(state="visible", timeout=10000)
                input_loc = combined_loc

        # Type query
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

        # Submit
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

        # Stream polling
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
            if cur_len > 20 and cur_len == last_len and not is_generating:
                stable_count += 1
                if stable_count >= 2:
                    break
            else:
                stable_count = 0
                last_len = cur_len

        time.sleep(1)
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
        except Exception:
            pass

        raw_text = page.evaluate(r"""() => {
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
            raise RuntimeError("Empty response received from ChatGPT")

        try:
            source_buttons = page.locator('button:has-text("Searched"), button:has-text("Sources"), button[aria-label*="Sources"]')
            if source_buttons.count() > 0 and source_buttons.first.is_visible():
                source_buttons.first.click(timeout=1500)
                time.sleep(0.5)
        except Exception:
            pass

        raw_links: List[str] = page.evaluate(
            """() => {
                const links = Array.from(document.querySelectorAll('a[href], [data-citation-url], [data-url], [data-testid*="citation"] a, button[data-url]'))
                    .map(el => el.href || el.getAttribute('data-citation-url') || el.getAttribute('data-url') || el.getAttribute('href'))
                    .filter(href => href && /^https?:/i.test(href) && !href.includes('chatgpt.com') && !href.includes('openai.com') && !href.includes('auth0.com'));
                return Array.from(new Set(links));
            }"""
        )
        unique_links = list(dict.fromkeys(raw_links))
        citations = [Citation.from_url(link, position=idx) for idx, link in enumerate(unique_links, 1)]

        duration = time.time() - start_time
        brand_cited = self.check_brand_presence(raw_text, brand_name)

        return AuditResult(
            platform=self.PLATFORM_NAME,
            account_id=account_id,
            query=query,
            brand_name=brand_name,
            brand_cited=brand_cited,
            citations=citations,
            raw_response_text=raw_text,
            response_length=len(raw_text),
            duration_seconds=round(duration, 2),
        )

    def run_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        account_name: Optional[str] = None,
        headless: bool = True,
    ) -> AuditResult:
        start_time = time.time()
        with Camoufox(headless=headless, humanize=True, geoip=False) as browser:
            storage_path = None
            if account_name:
                storage_path = self.session_manager.get_chatgpt_storage_path(account_name)

            context = browser.new_context(storage_state=str(storage_path) if storage_path else None)
            page = context.new_page()
            page.goto(self.BASE_URL, wait_until="domcontentloaded")
            time.sleep(2)
            self._dismiss_overlays(page)

            return self._execute_query_on_page(
                page=page,
                query=query,
                brand_name=brand_name,
                account_id=account_name or "guest",
                start_time=start_time,
            )
