from playwright.sync_api import Page, expect

from utils.config import BASE_URL
from utils.logger import get_logger


class AdminPage:

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

        self.page_heading = page.get_by_role(
            "heading",
            name="Admin Dashboard",
            exact=True,
        )

        self.current_user_text = page.locator(
            "div.product-meta"
        ).locator("div").nth(0)

        self.role_text = page.locator(
            "div.product-meta"
        ).locator("div").nth(1)

    def open(self):
        self.logger.info("Opening admin page")
        self.page.goto(f"{BASE_URL}/admin")

    def is_dashboard_visible(self) -> bool:
        return self.page_heading.is_visible()

    def assert_dashboard_visible(self):
        expect(self.page_heading).to_be_visible()

    def get_current_user_text(self) -> str:
        return self.current_user_text.inner_text().strip()

    def get_role_text(self) -> str:
        return self.role_text.inner_text().strip()