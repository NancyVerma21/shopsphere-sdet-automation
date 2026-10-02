from playwright.sync_api import Page

from pages.login_page import LoginPage


def test_login_page_opens(page: Page):
    login_page = LoginPage(page)

    login_page.open()

    assert login_page.get_title() == "ShopSphere - Online Shopping"