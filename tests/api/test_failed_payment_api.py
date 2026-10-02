import os
import uuid

import mysql.connector
import pytest
from dotenv import load_dotenv
from playwright.sync_api import APIRequestContext, Playwright
from werkzeug.security import generate_password_hash

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


def create_test_user():
    unique_id = uuid.uuid4().hex[:10]

    email = f"api_failed_payment_{unique_id}@example.com"
    password = "TestPassword@123"

    password_hash = generate_password_hash(password)

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users
            (
                first_name,
                last_name,
                email,
                password_hash,
                role,
                is_active
            )
            VALUES
            (%s, %s, %s, %s, %s, %s)
            """,
            (
                "API",
                f"Payment{unique_id}",
                email,
                password_hash,
                "customer",
                1,
            ),
        )

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return {
        "email": email,
        "password": password,
    }


def get_user_id(email: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,),
        )

        row = cursor.fetchone()

        return row[0] if row else None

    finally:
        cursor.close()
        connection.close()


def get_order_count(user_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE user_id = %s
            """,
            (user_id,),
        )

        return cursor.fetchone()[0]

    finally:
        cursor.close()
        connection.close()


def get_payment_count(user_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM payments p
            INNER JOIN orders o
                ON p.order_id = o.id
            WHERE o.user_id = %s
            """,
            (user_id,),
        )

        return cursor.fetchone()[0]

    finally:
        cursor.close()
        connection.close()


def get_cart_item(email: str, sku: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                ci.id,
                ci.quantity,
                ci.unit_price
            FROM cart_items ci
            INNER JOIN carts c
                ON ci.cart_id = c.id
            INNER JOIN users u
                ON c.user_id = u.id
            INNER JOIN products p
                ON ci.product_id = p.id
            WHERE u.email = %s
              AND p.sku = %s
              AND c.status = 'active'
            ORDER BY ci.id DESC
            LIMIT 1
            """,
            (email, sku),
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def cleanup_test_user(email: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,),
        )

        user_row = cursor.fetchone()

        if not user_row:
            return

        user_id = user_row[0]

        cursor.execute(
            """
            SELECT id
            FROM orders
            WHERE user_id = %s
            """,
            (user_id,),
        )

        order_ids = [
            row[0]
            for row in cursor.fetchall()
        ]

        if order_ids:
            placeholders = ",".join(
                ["%s"] * len(order_ids)
            )

            cursor.execute(
                f"""
                DELETE FROM payments
                WHERE order_id IN ({placeholders})
                """,
                tuple(order_ids),
            )

            cursor.execute(
                f"""
                DELETE FROM order_items
                WHERE order_id IN ({placeholders})
                """,
                tuple(order_ids),
            )

            cursor.execute(
                f"""
                DELETE FROM orders
                WHERE id IN ({placeholders})
                """,
                tuple(order_ids),
            )

        cursor.execute(
            """
            SELECT id
            FROM carts
            WHERE user_id = %s
            """,
            (user_id,),
        )

        cart_ids = [
            row[0]
            for row in cursor.fetchall()
        ]

        if cart_ids:
            placeholders = ",".join(
                ["%s"] * len(cart_ids)
            )

            cursor.execute(
                f"""
                DELETE FROM cart_items
                WHERE cart_id IN ({placeholders})
                """,
                tuple(cart_ids),
            )

            cursor.execute(
                f"""
                DELETE FROM carts
                WHERE id IN ({placeholders})
                """,
                tuple(cart_ids),
            )

        cursor.execute(
            """
            DELETE FROM addresses
            WHERE user_id = %s
            """,
            (user_id,),
        )

        cursor.execute(
            """
            DELETE FROM users
            WHERE id = %s
            """,
            (user_id,),
        )

        connection.commit()

    finally:
        cursor.close()
        connection.close()


@pytest.fixture
def api_context(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=BASE_URL
    )

    yield context

    context.dispose()


def login_user(
    api_context: APIRequestContext,
    user: dict,
):
    response = api_context.post(
        "/login",
        form={
            "email": user["email"],
            "password": user["password"],
        },
        max_redirects=0,
    )

    assert response.status == 302


def add_product_to_cart(
    api_context: APIRequestContext,
    sku: str,
):
    response = api_context.post(
        f"/cart/add/{sku}",
        max_redirects=0,
    )

    assert response.status == 302


def complete_checkout(
    api_context: APIRequestContext,
):
    return api_context.post(
        "/checkout",
        form={
            "address_choice": "new",
            "recipient_name": "API Tester",
            "line1": "123 Test Street",
            "line2": "",
            "city": "Patna",
            "state": "Bihar",
            "postal_code": "800001",
            "country": "India",
            "phone": "9876543210",
            "payment_method": "CARD",
        },
        max_redirects=0,
    )


def prepare_payment(
    api_context: APIRequestContext,
    user: dict,
):
    login_user(
        api_context,
        user,
    )

    add_product_to_cart(
        api_context,
        "P001",
    )

    checkout_response = complete_checkout(
        api_context,
    )

    assert checkout_response.status == 302

    location = checkout_response.headers.get(
        "location",
        "",
    )

    assert "/payment" in location


def test_failed_card_payment_does_not_persist_changes(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        prepare_payment(
            api_context,
            user,
        )

        user_id = get_user_id(
            user["email"],
        )

        assert user_id is not None

        orders_before = get_order_count(
            user_id,
        )

        payments_before = get_payment_count(
            user_id,
        )

        cart_before = get_cart_item(
            user["email"],
            "P001",
        )

        assert cart_before is not None

        response = api_context.post(
            "/payment",
            form={
                "payment_method": "CARD",
                "card_number": "4111111111110002",
                "expiry": "12/30",
                "cvv": "123",
            },
            max_redirects=0,
        )

        assert response.status == 302

        location = response.headers.get(
            "location",
            "",
        )

        assert "/payment" in location

        payment_page = api_context.get(
            "/payment",
        )

        assert payment_page.status == 200

        body = payment_page.text()

        assert (
            "Payment declined by the test payment gateway."
            in body
        )

        orders_after = get_order_count(
            user_id,
        )

        payments_after = get_payment_count(
            user_id,
        )

        cart_after = get_cart_item(
            user["email"],
            "P001",
        )

        assert orders_after == orders_before
        assert payments_after == payments_before

        assert cart_after is not None
        assert (
            cart_after["quantity"]
            == cart_before["quantity"]
        )

    finally:
        cleanup_test_user(user["email"])


def test_failed_upi_payment_does_not_persist_changes(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        prepare_payment(
            api_context,
            user,
        )

        user_id = get_user_id(
            user["email"],
        )

        assert user_id is not None

        orders_before = get_order_count(
            user_id,
        )

        payments_before = get_payment_count(
            user_id,
        )

        cart_before = get_cart_item(
            user["email"],
            "P001",
        )

        assert cart_before is not None

        response = api_context.post(
            "/payment",
            form={
                "payment_method": "UPI",
                "upi_id": "fail@upi",
            },
            max_redirects=0,
        )

        assert response.status == 302

        location = response.headers.get(
            "location",
            "",
        )

        assert "/payment" in location

        payment_page = api_context.get(
            "/payment",
        )

        assert payment_page.status == 200

        body = payment_page.text()

        assert (
            "Payment declined by the test payment gateway."
            in body
        )

        orders_after = get_order_count(
            user_id,
        )

        payments_after = get_payment_count(
            user_id,
        )

        cart_after = get_cart_item(
            user["email"],
            "P001",
        )

        assert orders_after == orders_before
        assert payments_after == payments_before

        assert cart_after is not None
        assert (
            cart_after["quantity"]
            == cart_before["quantity"]
        )

    finally:
        cleanup_test_user(user["email"])


def test_invalid_payment_method_is_rejected(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        prepare_payment(
            api_context,
            user,
        )

        user_id = get_user_id(
            user["email"],
        )

        assert user_id is not None

        orders_before = get_order_count(
            user_id,
        )

        payments_before = get_payment_count(
            user_id,
        )

        response = api_context.post(
            "/payment",
            form={
                "payment_method": "BITCOIN",
            },
            max_redirects=0,
        )

        assert response.status == 302

        location = response.headers.get(
            "location",
            "",
        )

        assert "/payment" in location

        payment_page = api_context.get(
            "/payment",
        )

        assert payment_page.status == 200

        body = payment_page.text()

        assert "Invalid payment method." in body

        orders_after = get_order_count(
            user_id,
        )

        payments_after = get_payment_count(
            user_id,
        )

        assert orders_after == orders_before
        assert payments_after == payments_before

    finally:
        cleanup_test_user(user["email"])