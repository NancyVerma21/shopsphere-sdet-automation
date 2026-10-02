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
                f"CancelTest{unique_id}",
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


def create_test_order(
    user_id: int,
    status: str,
    quantity: int = 1,
):
    order_number = (
        f"API-CANCEL-{uuid.uuid4().hex[:12].upper()}"
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        unit_price = Decimal("799.00")
        subtotal = unit_price * quantity
        shipping_charge = Decimal("99.00")
        total_amount = subtotal + shipping_charge

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
                status,
                subtotal,
                shipping_charge,
                total_amount,
                "API Cancel Tester",
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
                quantity,
                unit_price,
                unit_price * quantity,
            ),
        )

        connection.commit()

        return {
            "order_id": order_id,
            "order_number": order_number,
            "quantity": quantity,
        }

    finally:
        cursor.close()
        connection.close()


def get_order_status(order_number: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT status
            FROM orders
            WHERE order_number = %s
            """,
            (order_number,),
        )

        row = cursor.fetchone()

        return row[0] if row else None

    finally:
        cursor.close()
        connection.close()


def get_product_stock(sku: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT stock_qty
            FROM products
            WHERE sku = %s
            """,
            (sku,),
        )

        row = cursor.fetchone()

        return row[0] if row else None

    finally:
        cursor.close()
        connection.close()


def set_product_stock(sku: str, stock_qty: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE products
            SET stock_qty = %s
            WHERE sku = %s
            """,
            (
                stock_qty,
                sku,
            ),
        )

        connection.commit()

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


def test_customer_cannot_cancel_another_users_order(
    playwright: Playwright,
):
    owner = create_test_user("owner")
    attacker = create_test_user("attacker")

    attacker_context = None

    original_stock = get_product_stock("P001")

    try:
        owner_id = get_user_id(
            owner["email"],
        )

        assert owner_id is not None

        order = create_test_order(
            user_id=owner_id,
            status="PLACED",
            quantity=1,
        )

        attacker_context = playwright.request.new_context(
            base_url=BASE_URL
        )

        login_user(
            attacker_context,
            attacker,
        )

        response = attacker_context.post(
            f"/orders/{order['order_number']}/cancel",
            max_redirects=0,
        )

        # Expected secure behavior:
        # another customer must not be able to cancel
        # an order they do not own.
        #
        # The current AUT is expected to fail this assertion
        # because the cancellation query checks only the
        # order number.

        assert response.status in (
            301,
            302,
            403,
            404,
        ), (
            "Customer was able to cancel another user's order. "
            f"Unexpected HTTP status: {response.status}"
        )

        final_status = get_order_status(
            order["order_number"],
        )

        assert final_status == "PLACED", (
            "Another customer changed the order status. "
            f"Actual status: {final_status}"
        )

        final_stock = get_product_stock("P001")

        assert final_stock == original_stock, (
            "Unauthorized cancellation changed inventory. "
            f"Stock before: {original_stock}, "
            f"Stock after: {final_stock}"
        )

    finally:
        if attacker_context:
            attacker_context.dispose()

        set_product_stock(
            "P001",
            original_stock,
        )

        cleanup_user(owner["email"])
        cleanup_user(attacker["email"])


def test_cancelled_order_cannot_be_cancelled_again(
    playwright: Playwright,
):
    user = create_test_user("cancelled")

    api_context = None

    original_stock = get_product_stock("P001")

    try:
        user_id = get_user_id(
            user["email"],
        )

        assert user_id is not None

        order = create_test_order(
            user_id=user_id,
            status="CANCELLED",
            quantity=1,
        )

        api_context = playwright.request.new_context(
            base_url=BASE_URL
        )

        login_user(
            api_context,
            user,
        )

        response = api_context.post(
            f"/orders/{order['order_number']}/cancel",
            max_redirects=0,
        )

        assert response.status == 302

        final_status = get_order_status(
            order["order_number"],
        )

        # Expected behavior:
        # a CANCELLED order should remain CANCELLED and
        # inventory must not be restored again.
        assert final_status == "CANCELLED"

        final_stock = get_product_stock("P001")

        assert final_stock == original_stock, (
            "Repeated cancellation restored inventory. "
            f"Stock before: {original_stock}, "
            f"Stock after: {final_stock}"
        )

    finally:
        if api_context:
            api_context.dispose()

        set_product_stock(
            "P001",
            original_stock,
        )

        cleanup_user(user["email"])