import tempfile
import time
from typing import List, Optional
from camoufox.sync_api import Camoufox
from engine.drivers.base import BaseDriver, LoginWallException
from engine.models import AuditResult, Citation
from engine.session_manager import SessionManager


class GeminiDriver(BaseDriver):
    PLATFORM_NAME = "gemini"
    BASE_URL = "https://gemini.google.com/app"

    def authenticate(self, account_name: str) -> None:
        profile_dir = self.session_manager.get_gemini_profile_dir(account_name)
        with Camoufox(headless=False, humanize=True, persistent_context=True, user_data_dir=str(profile_dir)) as context:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(self.BASE_URL)

            # If not logged in and "Sign in" button is visible, click it to prompt user login
            time.sleep(2)
            login_btn = page.locator("a:has-text('Sign in'), button:has-text('Sign in'), a[href*='ServiceLogin'], a[href*='accounts.google.com']")
            if login_btn.count() > 0 and login_btn.first.is_visible():
                try:
                    login_btn.first.click()
                except Exception:
                    pass

            # Wait until actual Google authentication tokens and user profile are present
            max_wait = 300  # 5 minutes
            start = time.time()
            logged_in = False

            while time.time() - start < max_wait:
                cookies = context.cookies()
                has_auth_cookie = any(
                    c.get("name") in ["__Secure-1PSID", "__Secure-3PSID", "SID", "SAPISID", "HSID", "SSID"]
                    for c in cookies
                )
                has_profile_avatar = (
                    page.locator("a[aria-label*='Google Account'], a[href*='SignOutOptions'], button[aria-label*='Google Account'], img[alt*='Google Account'], [data-account-id]").count() > 0
                )
                is_on_app = "gemini.google.com/app" in page.url.lower()

                # Require auth cookies AND profile avatar or app landing without sign-in prompts
                if has_auth_cookie and (has_profile_avatar or (is_on_app and not page.locator("a:has-text('Sign in'), button:has-text('Sign in')").is_visible())):
                    logged_in = True
                    break

                time.sleep(1)

            if not logged_in:
                raise TimeoutError("Gemini login timed out. No active Google session detected within 5 minutes.")

            time.sleep(2)

    def _execute_gemini_session(
        self,
        context,
        query: str,
        brand_name: Optional[str] = None,
        account_id: str = "guest",
        start_time: float = 0.0,
    ) -> AuditResult:
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(self.BASE_URL, wait_until="domcontentloaded")

        time.sleep(2)
        # Check if guest mode is blocked by mandatory sign-in redirect
        if "accounts.google.com" in page.url.lower():
            raise LoginWallException("Redirected to Google Accounts login wall")

        input_sel = "rich-textarea, div[contenteditable='true'], textarea"
        try:
            page.wait_for_selector(input_sel, timeout=15000)
        except Exception as e:
            raise LoginWallException(f"Gemini input prompt not accessible: {e}")

        try:
            page.click(input_sel)
        except Exception:
            page.locator(input_sel).first.focus()

        # Safe text insertion for single-line queries and multiline meta-prompts
        try:
            page.keyboard.insert_text(query)
        except Exception:
            page.keyboard.type(query, delay=10)

        time.sleep(0.5)

        # Send prompt
        try:
            send_btn = page.locator('button[aria-label*="Send"], button.send-button, [data-testid="send-button"]').locator("visible=true").first
            if send_btn.is_visible():
                send_btn.click()
            else:
                page.keyboard.press("Enter")
        except Exception:
            page.keyboard.press("Enter")

        # Wait for response completion
        time.sleep(8)
        try:
            page.wait_for_selector('button[aria-label*="Stop"]', state="detached", timeout=60000)
        except Exception:
            pass

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
        citations = [Citation.from_url(link) for link in list(dict.fromkeys(raw_links))]
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

    def _run_guest_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        headless: bool = True,
    ) -> AuditResult:
        start_time = time.time()
        with tempfile.TemporaryDirectory() as temp_dir:
            with Camoufox(headless=headless, humanize=True, persistent_context=True, user_data_dir=temp_dir) as context:
                return self._execute_gemini_session(
                    context=context,
                    query=query,
                    brand_name=brand_name,
                    account_id="guest",
                    start_time=start_time,
                )

    def _run_authenticated_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        account_name: Optional[str] = None,
        headless: bool = True,
    ) -> AuditResult:
        if not account_name:
            account_name = self.session_manager.get_next_available_account(self.PLATFORM_NAME)
        if not account_name:
            raise RuntimeError("No available Gemini accounts found. Run 'auth' first.")

        profile_dir = self.session_manager.get_gemini_profile_dir(account_name)
        start_time = time.time()

        with Camoufox(headless=headless, humanize=True, persistent_context=True, user_data_dir=str(profile_dir)) as context:
            # Check auth status
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(self.BASE_URL, wait_until="domcontentloaded")
            time.sleep(2)
            cookies = context.cookies()
            has_auth_cookie = any(
                c.get("name") in ["__Secure-1PSID", "__Secure-3PSID", "SID", "SAPISID", "HSID", "SSID"]
                for c in cookies
            )
            has_signin_button = page.locator("a:has-text('Sign in'), button:has-text('Sign in'), a[href*='ServiceLogin']").is_visible()

            if not has_auth_cookie or has_signin_button:
                raise RuntimeError(
                    f"Gemini account '{account_name}' is not authenticated.\n"
                    f"Please run interactive login first:\n"
                    f"  uv run persuaid-geo auth --platform gemini --account {account_name}"
                )

            return self._execute_gemini_session(
                context=context,
                query=query,
                brand_name=brand_name,
                account_id=account_name,
                start_time=start_time,
            )

    def run_query(
        self,
        query: str,
        brand_name: Optional[str] = None,
        account_name: Optional[str] = None,
        headless: bool = True,
    ) -> AuditResult:
        # If user explicitly requested an account, run directly with it
        if account_name:
            return self._run_authenticated_query(
                query=query,
                brand_name=brand_name,
                account_name=account_name,
                headless=headless,
            )

        # Otherwise, try unauthenticated guest mode first
        try:
            return self._run_guest_query(
                query=query,
                brand_name=brand_name,
                headless=headless,
            )
        except Exception as e:
            avail_acc = self.session_manager.get_next_available_account(self.PLATFORM_NAME)
            if not avail_acc:
                raise RuntimeError(
                    f"Gemini guest mode was restricted ({e}), and no authenticated accounts are available.\n"
                    f"Please run: uv run persuaid-geo auth --platform gemini --account acc1"
                )
            print(f"⚠️ Guest access restricted ({e}). Falling back to authenticated account '{avail_acc}'...")
            return self._run_authenticated_query(
                query=query,
                brand_name=brand_name,
                account_name=avail_acc,
                headless=headless,
            )

