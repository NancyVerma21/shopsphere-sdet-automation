from playwright.sync_api import Page


def test_browser_opens(page: Page):
    page.goto("https://example.com")

    assert page.title() == "Example Domain"