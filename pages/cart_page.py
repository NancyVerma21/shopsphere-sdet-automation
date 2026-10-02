from decimal import Decimal

from playwright.sync_api import Page, expect

from utils.logger import get_logger


class CartPage:

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

        self.cart_items = page.locator(
            ".cart-item-card"
        )

        self.cart_subtotal = page.locator(
            ".summary-row"
        ).filter(
            has_text="Subtotal"
        ).locator("strong")

        self.cart_total = page.locator(
            ".summary-total strong"
        )

        self.empty_cart_message = page.get_by_text(
            "Your cart is empty",
            exact=True,
        )

    def open(self, base_url: str):
        self.logger.info("Opening cart page")

        self.page.goto(
            f"{base_url}/cart"
        )

    def get_item_count(self) -> int:
        return self.cart_items.count()

    def get_quantity(self, product_name: str) -> int:
        item = self.cart_items.filter(
            has_text=product_name
        )

        quantity_input = item.locator(
            "input[name='quantity']"
        )

        return int(
            quantity_input.input_value()
        )

    def get_item_unit_price(
        self,
        product_name: str,
    ) -> Decimal:

        item = self.cart_items.filter(
            has_text=product_name
        )

        price_text = item.locator(
            ".cart-unit-price"
        ).inner_text()

        return Decimal(
            price_text
            .replace("₹", "")
            .replace("each", "")
            .replace(",", "")
            .strip()
        )

    def get_item_total(
        self,
        product_name: str,
    ) -> Decimal:

        item = self.cart_items.filter(
            has_text=product_name
        )

        total_text = item.locator(
            ".cart-item-total"
        ).inner_text()

        return Decimal(
            total_text
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

    def get_subtotal(self) -> Decimal:

        text = self.cart_subtotal.inner_text()

        return Decimal(
            text
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

    def get_total(self) -> Decimal:

        text = self.cart_total.inner_text()

        return Decimal(
            text
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

    def update_quantity(
        self,
        product_name: str,
        quantity: int,
    ):

        item = self.cart_items.filter(
            has_text=product_name
        )

        quantity_input = item.locator(
            "input[name='quantity']"
        )

        quantity_input.fill(
            str(quantity)
        )

        item.get_by_role(
            "button",
            name="Update",
        ).click()

    def remove_item(
        self,
        product_name: str,
    ):

        item = self.cart_items.filter(
            has_text=product_name
        )

        item.get_by_role(
            "button",
            name="Remove",
        ).click()

    def expect_product_visible(
        self,
        product_name: str,
    ):

        item = self.cart_items.filter(
            has_text=product_name
        )

        expect(item).to_be_visible()

    def expect_product_not_visible(
        self,
        product_name: str,
    ):

        item = self.cart_items.filter(
            has_text=product_name
        )

        expect(item).to_have_count(0)