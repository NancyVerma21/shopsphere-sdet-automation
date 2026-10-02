from decimal import Decimal

from playwright.sync_api import Page, expect

from utils.config import BASE_URL
from utils.logger import get_logger


class ProductsPage:

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

        self.search_input = page.get_by_label("Search")
        self.category_select = page.get_by_label("Category")
        self.sort_select = page.get_by_label("Sort")

        self.apply_filter_button = page.get_by_role(
            "button",
            name="Apply Filters",
        )

        self.product_cards = page.locator(".product-card")

    def open(self):
        self.logger.info("Opening products page")

        self.page.goto(
            f"{BASE_URL}/products"
        )

    def search(self, search_text: str):
        self.logger.info(
            "Searching products with text: %s",
            search_text,
        )

        self.search_input.fill(search_text)
        self.apply_filter_button.click()

    def select_category(self, category: str):
        self.logger.info(
            "Selecting category: %s",
            category,
        )

        self.category_select.select_option(
            label=category
        )

        self.apply_filter_button.click()

    def select_sort(self, sort_value: str):
        self.logger.info(
            "Selecting sort option: %s",
            sort_value,
        )

        self.sort_select.select_option(
            sort_value
        )

        self.apply_filter_button.click()

    def get_product_count(self) -> int:
        return self.product_cards.count()

    def get_product_names(self) -> list[str]:
        names = self.page.locator(
            ".product-name a"
        ).all_inner_texts()

        return [
            name.strip()
            for name in names
        ]

    def get_product_prices(self) -> list[Decimal]:
        price_elements = self.page.locator(
            ".product-price"
        ).all_inner_texts()

        prices = []

        for price_text in price_elements:
            cleaned = (
                price_text
                .replace("₹", "")
                .replace(",", "")
                .strip()
            )

            prices.append(
                Decimal(cleaned)
            )

        return prices

    def product_is_visible(
        self,
        product_name: str,
    ):
        product = self.page.locator(
            ".product-card"
        ).filter(
            has_text=product_name
        )

        expect(product).to_be_visible()

    def open_product(
        self,
        product_name: str,
    ):
        self.logger.info(
            "Opening product: %s",
            product_name,
        )

        product_card = self.page.locator(
            ".product-card"
        ).filter(
            has_text=product_name
        ).first

        product_card.locator(
            ".product-name a"
        ).click()