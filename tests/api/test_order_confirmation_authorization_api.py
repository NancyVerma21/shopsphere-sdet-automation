import os
import uuid
from decimal import Decimal

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


def create_test_user(prefix: str):
    unique_id = uuid.uuid4().hex[:10]

    email = f"{prefix}_{unique_id}@example.com"
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
                prefix.capitalize(),
                f"ConfirmationTest{unique_id}",
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


def create_test_order(user_id: int):
    order_number = (
        f"API-CONF-{uuid.uuid4().hex[:12].upper()}"
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        subtotal = Decimal("799.00")
        shipping_charge = Decimal("99.00")
        total_amount = Decimal("898.00")

        cursor.execute(
            """
            INSERT INTO orders
            (
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
            VALUES
            (
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
                "PLACED",
                subtotal,
                shipping_charge,
                total_amount,
                "API Confirmation Tester",
                "123 Test Street",
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
            INSERT INTO order_items
            (
                order_id,
                product_id,
                product_name,
                quantity,
                unit_price,
                line_total
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                order_id,
                1,
                "Wireless Mouse",
                1,
                subtotal,
                subtotal,
            ),
        )

        connection.commit()

        return {
            "order_id": order_id,
            "order_number": order_number,
        }

    finally:
        cursor.close()
        connection.close()


def cleanup_user(email: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,),
        )

        row = cursor.fetchone()

        if not row:
            return

        user_id = row[0]

        cursor.execute(
            """
            SELECT id
            FROM orders
            WHERE user_id = %s
            """,
            (user_id,),
        )

        order_ids = [
            item[0]
            for item in cursor.fetchall()
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
            DELETE ci
            FROM cart_items ci
            INNER JOIN carts c
                ON ci.cart_id = c.id
            WHERE c.user_id = %s
            """,
            (user_id,),
        )

        cursor.execute(
            """
            DELETE FROM carts
            WHERE user_id = %s
            """,
            (user_id,),
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


def test_order_owner_can_view_order_confirmation(
    api_context: APIRequestContext,
):
    owner = create_test_user("owner")

    try:
        owner_id = get_user_id(
            owner["email"],
        )

        assert owner_id is not None

        order = create_test_order(
            owner_id,
        )

        login_user(
            api_context,
            owner,
        )

        response = api_context.get(
            f"/order-confirmation/{order['order_number']}",
            max_redirects=0,
        )

        assert response.status == 200

        body = response.text()

        assert order["order_number"] in body
        assert "Thank you for your order!" in body
        assert "ORDER CONFIRMED" in body

    finally:
        cleanup_user(owner["email"])


def test_customer_cannot_view_another_users_order_confirmation(
    playwright: Playwright,
):
    owner = create_test_user("owner")
    attacker = create_test_user("attacker")

    owner_context = None
    attacker_context = None

    try:
        owner_id = get_user_id(
            owner["email"],
        )

        assert owner_id is not None

        order = create_test_order(
            owner_id,
        )

        owner_context = playwright.request.new_context(
            base_url=BASE_URL
        )

        attacker_context = playwright.request.new_context(
            base_url=BASE_URL
        )

        login_user(
            owner_context,
            owner,
        )

        login_user(
            attacker_context,
            attacker,
        )

        owner_response = owner_context.get(
            f"/order-confirmation/{order['order_number']}",
            max_redirects=0,
        )

        assert owner_response.status == 200

        attacker_response = attacker_context.get(
            f"/order-confirmation/{order['order_number']}",
            max_redirects=0,
        )

        # Expected secure behavior:
        # an authenticated customer must not be able to view
        # another customer's order confirmation.
        #
        # The current AUT allows this and therefore this assertion
        # intentionally fails when BUG-013 is present.

        assert attacker_response.status in (
            301,
            302,
            403,
            404,
        ), (
            "Another customer was allowed to access "
            "the order confirmation. "
            f"Unexpected HTTP status: "
            f"{attacker_response.status}"
        )

        if attacker_response.status in (301, 302):
            location = attacker_response.headers.get(
                "location",
                "",
            )

            assert (
                "/orders" in location
                or "/login" in location
            )

    finally:
        if owner_context:
            owner_context.dispose()

        if attacker_context:
            attacker_context.dispose()

        cleanup_user(owner["email"])
        cleanup_user(attacker["email"])