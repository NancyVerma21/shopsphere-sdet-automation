from playwright.sync_api import Page

from utils.config import BASE_URL
from utils.logger import get_logger


class PaymentPage:

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

        self.card_number = page.get_by_label(
            "Card Number",
            exact=True,
        )

        self.expiry = page.get_by_label(
            "Expiry",
            exact=True,
        )

        self.cvv = page.get_by_label(
            "CVV",
            exact=True,
        )

        self.place_order_button = page.get_by_role(
            "button",
            name="Place Order",
        )

    def open(self):
        self.logger.info("Opening payment page")

        self.page.goto(
            f"{BASE_URL}/payment"
        )

    def fill_card(
        self,
        card_number: str,
        expiry: str,
        cvv: str,
    ):

        self.logger.info(
            "Entering card payment details"
        )

        self.card_number.fill(
            card_number
        )

        self.expiry.fill(
            expiry
        )

        self.cvv.fill(
            cvv
        )

    def place_order(self):

        self.logger.info(
            "Clicking Place Order"
        )

        self.place_order_button.click()