from playwright.sync_api import Page

from utils.config import BASE_URL
from utils.logger import get_logger


class OrdersPage:

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

        self.orders_list = page.locator(
            "section.orders-list"
        )

        self.order_cards = page.locator(
            "article.order-card"
        )

        self.empty_state = page.locator(
            "div.empty-state"
        )

        self.page_heading = page.get_by_role(
            "heading",
            name="My Orders",
            exact=True,
        )

    def open(self):

        self.logger.info(
            "Opening orders page"
        )

        self.page.goto(
            f"{BASE_URL}/orders"
        )

    def get_order_count(self) -> int:

        return self.order_cards.count()

    def get_order_numbers(self):

        numbers = []

        count = self.order_cards.count()

        for index in range(count):

            card = self.order_cards.nth(index)

            order_number = (
                card.locator("h2")
                .inner_text()
                .strip()
            )

            numbers.append(
                order_number
            )

        return numbers

    def get_order_card(
        self,
        order_number: str,
    ):

        return self.order_cards.filter(
            has_text=order_number
        ).first

    def get_order_status(
        self,
        order_number: str,
    ) -> str:

        card = self.get_order_card(
            order_number
        )

        return (
            card.locator(
                ".order-status"
            )
            .inner_text()
            .strip()
        )

    def get_order_total(
        self,
        order_number: str,
    ) -> str:

        card = self.get_order_card(
            order_number
        )

        total = (
            card.locator(
                ".order-status-block strong"
            )
            .inner_text()
            .strip()
        )

        return total

    def is_cancel_button_visible(
        self,
        order_number: str,
    ) -> bool:

        card = self.get_order_card(
            order_number
        )

        return card.get_by_role(
            "button",
            name="Cancel Order",
            exact=True,
        ).is_visible()

    def cancel_order(
        self,
        order_number: str,
    ):

        self.logger.info(
            f"Attempting to cancel order: {order_number}"
        )

        card = self.get_order_card(
            order_number
        )

        card.get_by_role(
            "button",
            name="Cancel Order",
            exact=True,
        ).click()

        self.page.wait_for_load_state(
            "networkidle"
        )

    def open_order(
        self,
        order_number: str,
    ):

        self.logger.info(
            f"Opening order: {order_number}"
        )

        card = self.get_order_card(
            order_number
        )

        card.get_by_role(
            "link",
            name="View Order",
            exact=True,
        ).click()