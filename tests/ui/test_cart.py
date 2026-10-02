from decimal import Decimal
from uuid import uuid4

from playwright.sync_api import Page

from pages.cart_page import CartPage
from utils.config import BASE_URL


PRODUCT_SKU = "P001"
PRODUCT_NAME = "Wireless Mouse"


def create_logged_in_user(page: Page):

    email = f"cart_{uuid4().hex[:10]}@example.com"
    password = "Test@12345"

    # Registration
    page.goto(f"{BASE_URL}/register")

    page.get_by_label(
        "First Name",
        exact=True,
    ).fill("Cart")

    page.get_by_label(
        "Last Name",
        exact=True,
    ).fill("Tester")

    page.get_by_label(
        "Email",
        exact=True,
    ).fill(email)

    page.get_by_label(
        "Password",
        exact=True,
    ).fill(password)

    page.get_by_label(
        "Confirm Password",
        exact=True,
    ).fill(password)

    page.get_by_role(
        "button",
        name="Create Account",
    ).click()

    # Login
    page.get_by_label(
        "Email",
        exact=True,
    ).fill(email)

    page.get_by_label(
        "Password",
        exact=True,
    ).fill(password)

    page.get_by_role(
        "button",
        name="Login",
    ).click()

    return email, password


def add_product_to_cart(page: Page):

    page.goto(
        f"{BASE_URL}/products/{PRODUCT_SKU}"
    )

    page.get_by_role(
        "button",
        name="Add to Cart",
    ).click()


def test_add_product_to_cart(page: Page):

    create_logged_in_user(page)

    add_product_to_cart(page)

    cart = CartPage(page)

    cart.open(BASE_URL)

    assert cart.get_item_count() == 1

    cart.expect_product_visible(
        PRODUCT_NAME
    )

    assert cart.get_quantity(
        PRODUCT_NAME
    ) == 1


def test_adding_same_product_twice_increases_quantity(
    page: Page,
):

    create_logged_in_user(page)

    add_product_to_cart(page)
    add_product_to_cart(page)

    cart = CartPage(page)

    cart.open(BASE_URL)

    assert cart.get_item_count() == 1

    assert cart.get_quantity(
        PRODUCT_NAME
    ) == 2


def test_update_cart_quantity(page: Page):

    create_logged_in_user(page)

    add_product_to_cart(page)

    cart = CartPage(page)

    cart.open(BASE_URL)

    cart.update_quantity(
        PRODUCT_NAME,
        2,
    )

    assert cart.get_quantity(
        PRODUCT_NAME
    ) == 2


def test_cart_subtotal_is_calculated_correctly(
    page: Page,
):

    create_logged_in_user(page)

    add_product_to_cart(page)

    cart = CartPage(page)

    cart.open(BASE_URL)

    unit_price = cart.get_item_unit_price(
        PRODUCT_NAME
    )

    quantity = cart.get_quantity(
        PRODUCT_NAME
    )

    expected_subtotal = (
        unit_price * quantity
    )

    actual_subtotal = cart.get_subtotal()

    assert actual_subtotal == expected_subtotal


def test_cart_item_total_is_calculated_correctly(
    page: Page,
):

    create_logged_in_user(page)

    add_product_to_cart(page)

    cart = CartPage(page)

    cart.open(BASE_URL)

    unit_price = cart.get_item_unit_price(
        PRODUCT_NAME
    )

    quantity = cart.get_quantity(
        PRODUCT_NAME
    )

    expected_item_total = (
        unit_price * quantity
    )

    actual_item_total = cart.get_item_total(
        PRODUCT_NAME
    )

    assert actual_item_total == expected_item_total


def test_remove_product_from_cart(page: Page):

    create_logged_in_user(page)

    add_product_to_cart(page)

    cart = CartPage(page)

    cart.open(BASE_URL)

    cart.remove_item(
        PRODUCT_NAME
    )

    cart.expect_product_not_visible(
        PRODUCT_NAME
    )

    assert cart.empty_cart_message.is_visible()


def test_out_of_stock_product_cannot_be_added(
    page: Page,
):

    create_logged_in_user(page)

    page.goto(
        f"{BASE_URL}/products/P011"
    )

    out_of_stock_button = page.get_by_role(
        "button",
        name="Out of Stock",
    )

    assert out_of_stock_button.is_visible()

    assert out_of_stock_button.is_disabled()


def test_quantity_above_stock_is_rejected(
    page: Page,
):

    create_logged_in_user(page)

    add_product_to_cart(page)

    cart = CartPage(page)

    cart.open(BASE_URL)

    item = cart.cart_items.filter(
        has_text=PRODUCT_NAME
    )

    quantity_input = item.locator(
        "input[name='quantity']"
    )

    quantity_input.fill("999")

    action = item.locator(
        "form.quantity-form"
    ).get_attribute("action")

    assert action

    item_id = action.rstrip("/").split("/")[-1]

    response = page.request.post(
        f"{BASE_URL}/cart/update/{item_id}",
        form={
            "quantity": "999",
        },
    )

    assert response.ok

    cart.open(BASE_URL)

    actual_quantity = cart.get_quantity(
        PRODUCT_NAME
    )

    assert actual_quantity <= 44