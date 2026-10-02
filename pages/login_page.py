from playwright.sync_api import Page

from utils.config import BASE_URL
from utils.logger import get_logger


class LoginPage:

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Password")
        self.login_button = page.get_by_role("button", name="Login")

    def open(self):
        self.logger.info("Opening login page")
        self.page.goto(BASE_URL)

    def get_title(self):
        self.logger.info("Getting page title")
        return self.page.title()

    def login(self, email: str, password: str):
        self.logger.info("Entering login credentials")
        self.email_input.fill(email)
        self.password_input.fill(password)

        self.logger.info("Clicking login button")
        self.login_button.click()