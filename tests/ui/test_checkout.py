from uuid import uuid4
import os

import mysql.connector
from dotenv import load_dotenv
from playwright.sync_api import Page

from pages.checkout_page import CheckoutPage
from pages.payment_page import PaymentPage
from utils.config import BASE_URL


load_dotenv()

PRODUCT_SKU = "P001"


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def get_order_count_for_email(email: str) -> int:
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(o.id)
            FROM users u
            LEFT JOIN orders o
                ON o.user_id = u.id
            WHERE u.email = %s
            """,
            (email,),
        )

        result = cursor.fetchone()

        return int(result[0])

    finally:
        cursor.close()
        conn.close()


def get_latest_order_for_email(email: str):
    conn = get_db_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                o.id,
                o.order_number,
                o.status,
                o.subtotal,
                o.shipping_charge,
                o.total_amount,
                p.payment_status,
                p.payment_method,
                p.amount AS payment_amount,
                p.failure_reason
            FROM orders o
            INNER JOIN users u
                ON o.user_id = u.id
            LEFT JOIN payments p
                ON p.order_id = o.id
            WHERE u.email = %s
            ORDER BY o.id DESC
            LIMIT 1
            """,
            (email,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def get_latest_order_item_for_email(email: str):
    conn = get_db_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                oi.order_id,
                oi.product_id,
                oi.product_name,
                oi.quantity,
                oi.unit_price,
                oi.line_total
            FROM order_items oi
            INNER JOIN orders o
                ON oi.order_id = o.id
            INNER JOIN users u
                ON o.user_id = u.id
            WHERE u.email = %s
            ORDER BY oi.id DESC
            LIMIT 1
            """,
            (email,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def get_product_stock(sku: str) -> int:
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT stock_qty
            FROM products
            WHERE sku = %s
            """,
            (sku,),
        )

        result = cursor.fetchone()

        if result is None:
            raise AssertionError(
                f"Product with SKU {sku} was not found in the database."
            )

        return int(result[0])

    finally:
        cursor.close()
        conn.close()


def create_logged_in_user(page: Page):

    email = (
        f"checkout_{uuid4().hex[:10]}"
        "@example.com"
    )

    password = "Test@12345"

    page.goto(
        f"{BASE_URL}/register"
    )

    page.get_by_label(
        "First Name",
        exact=True,
    ).fill("Checkout")

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

    return email


def add_product_to_cart(page: Page):

    page.goto(
        f"{BASE_URL}/products/{PRODUCT_SKU}"
    )

    page.get_by_role(
        "button",
        name="Add to Cart",
    ).click()


def complete_checkout_address(
    page: Page,
):

    checkout = CheckoutPage(page)

    checkout.open()

    checkout.select_new_address()

    checkout.fill_address(
        recipient_name="Checkout Tester",
        phone="9876543210",
        line1="House 101, Main Road",
        line2="",
        city="Patna",
        state="Bihar",
        postal_code="800001",
        country="India",
    )

    checkout.select_card_payment()

    checkout.continue_to_payment()


def test_checkout_page_opens(page: Page):

    create_logged_in_user(page)

    add_product_to_cart(page)

    checkout = CheckoutPage(page)

    checkout.open()

    assert page.url.endswith(
        "/checkout"
    )

    assert page.get_by_role(
        "heading",
        name="Delivery Address",
    ).is_visible()


def test_continue_from_checkout_to_payment(
    page: Page,
):

    create_logged_in_user(page)

    add_product_to_cart(page)

    complete_checkout_address(page)

    assert page.url.endswith(
        "/payment"
    )

    assert page.get_by_role(
        "heading",
        name="Payment Details",
    ).is_visible()


def test_failed_card_payment_does_not_create_order(
    page: Page,
):

    email = create_logged_in_user(page)

    add_product_to_cart(page)

    complete_checkout_address(page)

    orders_before_payment = get_order_count_for_email(
        email
    )

    payment = PaymentPage(page)

    payment.fill_card(
        card_number="4111111111110002",
        expiry="12/30",
        cvv="123",
    )

    payment.place_order()

    assert page.url.endswith(
        "/payment"
    )

    assert page.get_by_text(
        "Payment declined by the test payment gateway."
    ).is_visible()

    assert not page.get_by_text(
        "Thank you for your order!"
    ).is_visible()

    orders_after_payment = get_order_count_for_email(
        email
    )

    latest_order = get_latest_order_for_email(
        email
    )

    assert orders_after_payment == orders_before_payment, (
        "Failed card payment created a new order unexpectedly.\n"
        f"Orders before payment: {orders_before_payment}\n"
        f"Orders after payment: {orders_after_payment}\n"
        f"Latest order: {latest_order}"
    )


def test_successful_card_payment_creates_order_and_updates_database(
    page: Page,
):

    email = create_logged_in_user(page)

    stock_before = get_product_stock(
        PRODUCT_SKU
    )

    orders_before_payment = get_order_count_for_email(
        email
    )

    add_product_to_cart(page)

    complete_checkout_address(page)

    payment = PaymentPage(page)

    payment.fill_card(
        card_number="4111111111111111",
        expiry="12/30",
        cvv="123",
    )

    payment.place_order()

    page.wait_for_load_state(
        "networkidle"
    )

    orders_after_payment = get_order_count_for_email(
        email
    )

    latest_order = get_latest_order_for_email(
        email
    )

    latest_order_item = get_latest_order_item_for_email(
        email
    )

    stock_after = get_product_stock(
        PRODUCT_SKU
    )

    page_text = page.locator(
        "body"
    ).inner_text()

    success_visible = page.get_by_text(
        "Thank you for your order!"
    ).is_visible()

    if not success_visible:

        raise AssertionError(
            "Successful card payment did not complete the expected "
            "order flow.\n\n"
            f"Current URL: {page.url}\n\n"
            f"Orders before payment: {orders_before_payment}\n"
            f"Orders after payment: {orders_after_payment}\n"
            f"Latest order: {latest_order}\n"
            f"Latest order item: {latest_order_item}\n"
            f"Stock before payment: {stock_before}\n"
            f"Stock after payment: {stock_after}\n\n"
            f"Payment page text:\n{page_text}"
        )

    assert orders_after_payment == (
        orders_before_payment + 1
    ), (
        "Successful payment did not create exactly one order.\n"
        f"Orders before payment: {orders_before_payment}\n"
        f"Orders after payment: {orders_after_payment}\n"
        f"Latest order: {latest_order}"
    )

    assert latest_order is not None

    assert latest_order["status"] == "PLACED"

    assert latest_order["payment_status"] == "SUCCESS"

    assert latest_order["payment_method"] == "CARD"

    assert latest_order["payment_amount"] == (
        latest_order["total_amount"]
    )

    assert latest_order_item is not None

    assert latest_order_item["quantity"] == 1

    assert latest_order_item["product_id"] is not None

    assert latest_order_item["unit_price"] > 0

    assert latest_order_item["line_total"] == (
        latest_order_item["unit_price"]
        * latest_order_item["quantity"]
    )

    assert stock_after == (
        stock_before - 1
    ), (
        "Product stock was not reduced by exactly one unit.\n"
        f"Stock before: {stock_before}\n"
        f"Stock after: {stock_after}"
    )