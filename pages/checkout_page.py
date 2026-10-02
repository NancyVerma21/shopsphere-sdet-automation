from playwright.sync_api import Page

from utils.config import BASE_URL
from utils.logger import get_logger


class CheckoutPage:

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

        self.new_address_radio = page.locator(
            "#new-address-choice"
        )

        self.recipient_name = page.get_by_label(
            "Recipient Name",
            exact=True,
        )

        self.phone = page.get_by_label(
            "Phone",
            exact=True,
        )

        self.line1 = page.get_by_label(
            "Address Line 1",
            exact=True,
        )

        self.line2 = page.get_by_label(
            "Address Line 2",
            exact=True,
        )

        self.city = page.get_by_label(
            "City",
            exact=True,
        )

        self.state = page.get_by_label(
            "State",
            exact=True,
        )

        self.postal_code = page.get_by_label(
            "Postal Code",
            exact=True,
        )

        self.country = page.get_by_label(
            "Country",
            exact=True,
        )

        self.card_payment_radio = page.locator(
            'input[name="payment_method"][value="CARD"]'
        )

        self.continue_button = page.get_by_role(
            "button",
            name="Continue to Payment",
        )

    def open(self):
        self.logger.info("Opening checkout page")

        self.page.goto(
            f"{BASE_URL}/checkout"
        )

    def select_new_address(self):

        self.logger.info(
            "Selecting new delivery address"
        )

        if self.new_address_radio.count() > 0:
            self.new_address_radio.check()

    def fill_address(
        self,
        recipient_name: str,
        phone: str,
        line1: str,
        city: str,
        state: str,
        postal_code: str,
        country: str = "India",
        line2: str = "",
    ):

        self.logger.info(
            "Filling checkout delivery address"
        )

        self.recipient_name.fill(
            recipient_name
        )

        self.phone.fill(
            phone
        )

        self.line1.fill(
            line1
        )

        # Address Line 2 is optional.
        # Some checkout layouts do not render it.
        if self.line2.count() > 0:
            self.line2.fill(
                line2
            )

        self.city.fill(
            city
        )

        self.state.fill(
            state
        )

        self.postal_code.fill(
            postal_code
        )

        self.country.fill(
            country
        )

    def select_card_payment(self):

        self.logger.info(
            "Selecting card payment"
        )

        self.card_payment_radio.check()

    def continue_to_payment(self):

        self.logger.info(
            "Continuing to payment"
        )

        self.continue_button.click()