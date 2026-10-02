import os
import re
import uuid
from decimal import Decimal

import mysql.connector
import pytest
from dotenv import load_dotenv
from playwright.sync_api import APIRequestContext, Playwright
from werkzeug.security import generate_password_hash

from utils.config import BASE_URL


load_dotenv()


TEST_PRODUCT_PRICE = Decimal("1000.00")
TEST_PRODUCT_STOCK = 10


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

    email = f"api_shipping_{unique_id}@example.com"
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
                f"Shipping{unique_id}",
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


def get_category_id():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id
            FROM categories
            WHERE is_active = TRUE
            ORDER BY id ASC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        return row[0] if row else None

    finally:
        cursor.close()
        connection.close()


def create_boundary_product():
    unique_id = uuid.uuid4().hex[:10].upper()

    sku = f"QA-SHIPPING-{unique_id}"
    name = f"Shipping Boundary Product {unique_id}"

    category_id = get_category_id()

    assert category_id is not None

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO products
            (
                sku,
                name,
                description,
                category_id,
                price,
                stock_qty,
                is_active
            )
            VALUES
            (
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
                sku,
                name,
                "Temporary QA product for shipping-boundary testing.",
                category_id,
                TEST_PRODUCT_PRICE,
                TEST_PRODUCT_STOCK,
                1,
            ),
        )

        connection.commit()

        return {
            "sku": sku,
            "name": name,
        }

    finally:
        cursor.close()
        connection.close()


def cleanup_product(sku: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM products WHERE sku = %s",
            (sku,),
        )

        row = cursor.fetchone()

        if not row:
            return

        product_id = row[0]

        # Remove any test cart items referencing this product.
        cursor.execute(
            """
            DELETE FROM cart_items
            WHERE product_id = %s
            """,
            (product_id,),
        )

        cursor.execute(
            """
            DELETE FROM products
            WHERE id = %s
            """,
            (product_id,),
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


def extract_shipping_amount(body: str) -> str:
    match = re.search(
        r"<span>\s*Shipping\s*</span>\s*"
        r"<strong>\s*₹?([\d,]+\.\d{2})\s*</strong>",
        body,
        flags=re.IGNORECASE,
    )

    assert match is not None, (
        "Could not locate the shipping amount in the checkout response."
    )

    return match.group(1).replace(",", "")


def extract_subtotal_amount(body: str) -> str:
    match = re.search(
        r"<span>\s*Subtotal\s*</span>\s*"
        r"<strong>\s*₹?([\d,]+\.\d{2})\s*</strong>",
        body,
        flags=re.IGNORECASE,
    )

    assert match is not None, (
        "Could not locate the subtotal amount in the checkout response."
    )

    return match.group(1).replace(",", "")


def test_exact_1000_subtotal_gets_free_shipping(
    api_context: APIRequestContext,
):
    user = create_test_user()
    product = create_boundary_product()

    try:
        login_user(
            api_context,
            user,
        )

        add_response = api_context.post(
            f"/cart/add/{product['sku']}",
            max_redirects=0,
        )

        assert add_response.status == 302

        checkout_response = api_context.get(
            "/checkout",
            max_redirects=0,
        )

        assert checkout_response.status == 200

        body = checkout_response.text()

        subtotal = extract_subtotal_amount(body)
        shipping = extract_shipping_amount(body)

        assert subtotal == "1000.00", (
            "Test setup did not produce the exact "
            f"₹1,000 subtotal. Actual subtotal: ₹{subtotal}"
        )

        # Canonical BUG-005 expectation:
        # exactly ₹1,000 should qualify for free shipping.
        #
        # The current AUT uses:
        #     subtotal > SHIPPING_THRESHOLD
        # instead of >=, so this assertion is expected
        # to fail for the buggy application.

        assert shipping == "0.00", (
            "Exactly ₹1,000 should receive free shipping, "
            f"but the AUT charged ₹{shipping}."
        )

    finally:
        cleanup_user(user["email"])
        cleanup_product(product["sku"])