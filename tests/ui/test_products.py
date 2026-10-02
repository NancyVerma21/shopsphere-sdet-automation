from playwright.sync_api import Page

from pages.products_page import ProductsPage


def test_products_page_loads(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    assert page.url.endswith("/products")
    assert products_page.get_product_count() == 11


def test_products_have_expected_names(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    product_names = products_page.get_product_names()

    assert "Wireless Mouse" in product_names
    assert "Mechanical Keyboard" in product_names
    assert "Cotton T-Shirt" in product_names
    assert "Bluetooth Speaker Mini" in product_names


def test_price_sort_low_to_high(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    products_page.select_sort("price_asc")

    prices = products_page.get_product_prices()

    assert prices == sorted(prices)


def test_price_sort_high_to_low(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    products_page.select_sort("price_desc")

    prices = products_page.get_product_prices()

    assert prices == sorted(
        prices,
        reverse=True,
    )


def test_search_product(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    products_page.search(
        "Wireless Mouse"
    )

    products_page.product_is_visible(
        "Wireless Mouse"
    )


def test_category_filter_electronics(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    products_page.select_category(
        "Electronics"
    )

    names = products_page.get_product_names()

    assert names
    assert "Wireless Mouse" in names
    assert "Mechanical Keyboard" in names


def test_out_of_stock_product_is_displayed(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    products_page.product_is_visible(
        "Bluetooth Speaker Mini"
    )

    product = page.locator(
        ".product-card"
    ).filter(
        has_text="Bluetooth Speaker Mini"
    )

    assert product.get_by_text(
        "Out of Stock"
    ).is_visible()


def test_product_details_navigation(page: Page):
    products_page = ProductsPage(page)

    products_page.open()

    products_page.open_product(
        "Wireless Mouse"
    )

    assert page.url.endswith(
        "/products/P001"
    )

    assert page.get_by_role(
        "heading",
        name="Wireless Mouse",
    ).is_visible()