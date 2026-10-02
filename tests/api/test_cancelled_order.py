import os
import uuid
from decimal import Decimal

import mysql.connector
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from werkzeug.security import generate_password_hash

from pages.login_page import LoginPage
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

    email = f"bug006_{unique_id}@example.com"
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
                "Bug006",
                f"Test{unique_id}",
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


def create_cancelled_order(user_id: int):
    order_number = (
        f"BUG006-{uuid.uuid4().hex[:12].upper()}"
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
                "CANCELLED",
                subtotal,
                shipping_charge,
                total_amount,
                "BUG006 Tester",
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

        return order_number

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


def test_cancel_button_hidden_for_cancelled_order(page: Page):
    user = create_test_user()

    try:
        user_id = get_user_id(user["email"])

        assert user_id is not None

        order_number = create_cancelled_order(user_id)

        login_page = LoginPage(page)

        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        login_page.login(
            email=user["email"],
            password=user["password"],
        )

        page.wait_for_load_state("networkidle")

        page.goto(f"{BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        order_card = page.locator(
            "article.order-card"
        ).filter(
            has_text=order_number
        )

        expect(order_card).to_be_visible()

        expect(
            order_card.locator(".order-status")
        ).to_have_text("CANCELLED")

        cancel_button = order_card.get_by_role(
            "button",
            name="Cancel Order",
            exact=True,
        )

        # Canonical BUG-006 expectation:
        # a CANCELLED order must not show a Cancel Order action.
        #
        # The current AUT renders the button for every order,
        # so this assertion is expected to fail.

        expect(cancel_button).not_to_be_visible()

    finally:
        cleanup_test_user(user["email"])