from uuid import uuid4
import os

import mysql.connector
from dotenv import load_dotenv
from playwright.sync_api import Page, Browser

from pages.orders_page import OrdersPage
from utils.config import BASE_URL


load_dotenv()


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def get_user_id(email: str) -> int:

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,),
        )

        result = cursor.fetchone()

        if result is None:
            raise AssertionError(
                f"Test user was not found: {email}"
            )

        return int(result[0])

    finally:
        cursor.close()
        conn.close()


def get_order_status_from_db(
    order_number: str,
):

    conn = get_db_connection()

    try:
        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                order_number,
                user_id,
                status,
                subtotal,
                shipping_charge,
                total_amount
            FROM orders
            WHERE order_number = %s
            """,
            (order_number,),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def create_logged_in_user(
    page: Page,
    prefix: str = "orders",
):

    email = (
        f"{prefix}_{uuid4().hex[:10]}"
        "@example.com"
    )

    password = "Test@12345"

    page.goto(
        f"{BASE_URL}/register"
    )

    page.get_by_label(
        "First Name",
        exact=True,
    ).fill("Orders")

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
        exact=True,
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
        exact=True,
    ).click()

    return email


def seed_order(
    email: str,
    status: str = "PLACED",
    payment_status: str = "SUCCESS",
):

    user_id = get_user_id(email)

    order_number = (
        "SS-TEST-"
        + uuid4().hex[:12].upper()
    )

    transaction_reference = (
        "TXN-"
        + uuid4().hex[:12].upper()
    )

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO orders (
                order_number,
                user_id,
                status,
                subtotal,
                shipping_charge,
                total_amount,
                shipping_recipient_name,
                shipping_line1,
                shipping_line2,
                shipping_city,
                shipping_state,
                shipping_postal_code,
                shipping_country,
                shipping_phone
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                order_number,
                user_id,
                status,
                "799.00",
                "99.00",
                "898.00",
                "Orders Tester",
                "House 101, Main Road",
                None,
                "Patna",
                "Bihar",
                "800001",
                "India",
                "9876543210",
            ),
        )

        order_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO order_items (
                order_id,
                product_id,
                product_name,
                quantity,
                unit_price,
                line_total
            )
            SELECT
                %s,
                p.id,
                p.name,
                1,
                p.price,
                p.price
            FROM products p
            WHERE p.sku = 'P001'
            """,
            (order_id,),
        )

        cursor.execute(
            """
            INSERT INTO payments (
                order_id,
                payment_method,
                payment_status,
                transaction_reference,
                amount
            )
            VALUES (
                %s,
                'CARD',
                %s,
                %s,
                %s
            )
            """,
            (
                order_id,
                payment_status,
                transaction_reference,
                "898.00",
            ),
        )

        conn.commit()

        return order_number

    finally:
        cursor.close()
        conn.close()


def test_orders_page_displays_seeded_order(
    page: Page,
):

    email = create_logged_in_user(
        page,
        prefix="orders_list",
    )

    order_number = seed_order(
        email,
        status="PLACED",
        payment_status="SUCCESS",
    )

    orders = OrdersPage(page)

    orders.open()

    assert page.url.endswith(
        "/orders"
    )

    assert orders.page_heading.is_visible()

    assert orders.get_order_count() == 1

    assert order_number in (
        orders.get_order_numbers()
    )

    assert orders.get_order_status(
        order_number
    ) == "PLACED"

    assert orders.get_order_total(
        order_number
    ).endswith("898.00")


def test_order_details_displays_seeded_order(
    page: Page,
):

    email = create_logged_in_user(
        page,
        prefix="orders_details",
    )

    order_number = seed_order(
        email,
        status="PLACED",
        payment_status="SUCCESS",
    )

    orders = OrdersPage(page)

    orders.open()

    orders.open_order(
        order_number
    )

    assert page.url.endswith(
        f"/orders/{order_number}"
    )

    assert page.get_by_role(
        "heading",
        name=order_number,
        exact=True,
    ).is_visible()

    assert page.get_by_text(
        "Wireless Mouse",
        exact=True,
    ).is_visible()

    assert page.get_by_text(
        "CARD",
        exact=True,
    ).is_visible()

    assert page.get_by_text(
        "SUCCESS",
        exact=True,
    ).is_visible()

    assert page.get_by_text(
        "Orders Tester",
        exact=True,
    ).is_visible()


def test_cancel_button_hidden_for_shipped_order(
    page: Page,
):

    email = create_logged_in_user(
        page,
        prefix="orders_shipped",
    )

    order_number = seed_order(
        email,
        status="SHIPPED",
        payment_status="SUCCESS",
    )

    orders = OrdersPage(page)

    orders.open()

    assert orders.get_order_status(
        order_number
    ) == "SHIPPED"

    assert not orders.is_cancel_button_visible(
        order_number
    ), (
        "Cancel Order button is visible for a "
        "SHIPPED order."
    )


def test_shipped_order_cannot_be_cancelled(
    page: Page,
):

    email = create_logged_in_user(
        page,
        prefix="orders_cancel_shipped",
    )

    order_number = seed_order(
        email,
        status="SHIPPED",
        payment_status="SUCCESS",
    )

    db_before = get_order_status_from_db(
        order_number
    )

    assert db_before is not None

    assert db_before["status"] == "SHIPPED"

    orders = OrdersPage(page)

    orders.open()

    assert orders.is_cancel_button_visible(
        order_number
    ), (
        "Expected the seeded AUT defect to expose "
        "Cancel Order for a SHIPPED order."
    )

    orders.cancel_order(
        order_number
    )

    db_after = get_order_status_from_db(
        order_number
    )

    assert db_after is not None

    assert db_after["status"] == "SHIPPED", (
        "SHIPPED order was cancelled unexpectedly.\n"
        f"Order number: {order_number}\n"
        f"Database state before: {db_before}\n"
        f"Database state after: {db_after}"
    )


def test_user_cannot_view_another_users_order(
    page: Page,
    browser: Browser,
):

    owner_email = create_logged_in_user(
        page,
        prefix="order_owner",
    )

    order_number = seed_order(
        owner_email,
        status="PLACED",
        payment_status="SUCCESS",
    )

    attacker_context = browser.new_context()

    attacker_page = attacker_context.new_page()

    try:

        create_logged_in_user(
            attacker_page,
            prefix="order_attacker",
        )

        attacker_page.goto(
            f"{BASE_URL}/orders/{order_number}"
        )

        body_text = (
            attacker_page.locator(
                "body"
            )
            .inner_text()
        )

        assert order_number not in body_text, (
            "Another authenticated customer can "
            "view an order they do not own."
        )

    finally:

        attacker_context.close()