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

    email = f"api_cart_{unique_id}@example.com"
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
                f"Cart{unique_id}",
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


def delete_test_user(email: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            DELETE ci
            FROM cart_items ci
            INNER JOIN carts c
                ON ci.cart_id = c.id
            INNER JOIN users u
                ON c.user_id = u.id
            WHERE u.email = %s
            """,
            (email,),
        )

        cursor.execute(
            """
            DELETE FROM carts
            WHERE user_id = (
                SELECT id
                FROM users
                WHERE email = %s
            )
            """,
            (email,),
        )

        cursor.execute(
            "DELETE FROM users WHERE email = %s",
            (email,),
        )

        connection.commit()

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
                ci.cart_id,
                ci.product_id,
                ci.quantity,
                ci.unit_price,
                p.stock_qty,
                p.sku
            FROM cart_items ci
            INNER JOIN carts c
                ON ci.cart_id = c.id
            INNER JOIN users u
                ON c.user_id = u.id
            INNER JOIN products p
                ON ci.product_id = p.id
            WHERE u.email = %s
              AND c.status = 'active'
              AND p.sku = %s
            ORDER BY ci.id DESC
            LIMIT 1
            """,
            (email, sku),
        )

        return cursor.fetchone()

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

    return response


def add_product_to_cart(
    api_context: APIRequestContext,
    sku: str,
):
    response = api_context.post(
        f"/cart/add/{sku}",
        max_redirects=0,
    )

    assert response.status == 302

    return response


def test_cart_api_rejects_quantity_above_stock(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        login_user(
            api_context,
            user,
        )

        add_product_to_cart(
            api_context,
            "P001",
        )

        item = get_cart_item(
            user["email"],
            "P001",
        )

        assert item is not None

        item_id = item["id"]
        stock_qty = item["stock_qty"]

        excessive_quantity = stock_qty + 1

        response = api_context.post(
            f"/cart/update/{item_id}",
            form={
                "quantity": str(excessive_quantity),
            },
            max_redirects=0,
        )

        assert response.status == 302

        updated_item = get_cart_item(
            user["email"],
            "P001",
        )

        assert updated_item is not None

        # Expected secure/business behavior:
        # quantity must never exceed available stock.
        #
        # The current AUT is expected to fail this assertion
        # because update_cart_item() does not perform an upper-bound
        # stock validation.

        assert updated_item["quantity"] <= stock_qty, (
            "Cart quantity exceeds available stock. "
            f"Requested: {excessive_quantity}, "
            f"Stock: {stock_qty}, "
            f"Actual cart quantity: {updated_item['quantity']}"
        )

    finally:
        delete_test_user(user["email"])


def test_cart_api_rejects_zero_quantity(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        login_user(
            api_context,
            user,
        )

        add_product_to_cart(
            api_context,
            "P001",
        )

        item = get_cart_item(
            user["email"],
            "P001",
        )

        assert item is not None

        item_id = item["id"]

        response = api_context.post(
            f"/cart/update/{item_id}",
            form={
                "quantity": "0",
            },
            max_redirects=0,
        )

        assert response.status == 302

        updated_item = get_cart_item(
            user["email"],
            "P001",
        )

        assert updated_item is not None

        # Expected secure/business behavior:
        # quantity 0 should be rejected.
        #
        # The current AUT is expected to fail this assertion
        # because quantity 0 is explicitly allowed by the route.

        assert updated_item["quantity"] >= 1, (
            "Cart accepted quantity 0. "
            f"Actual cart quantity: {updated_item['quantity']}"
        )

    finally:
        delete_test_user(user["email"])


def test_cart_api_rejects_negative_quantity(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        login_user(
            api_context,
            user,
        )

        add_product_to_cart(
            api_context,
            "P001",
        )

        item = get_cart_item(
            user["email"],
            "P001",
        )

        assert item is not None

        item_id = item["id"]

        response = api_context.post(
            f"/cart/update/{item_id}",
            form={
                "quantity": "-1",
            },
            max_redirects=0,
        )

        assert response.status == 302

        updated_item = get_cart_item(
            user["email"],
            "P001",
        )

        assert updated_item is not None

        assert updated_item["quantity"] == 1, (
            "Negative quantity changed the cart item. "
            f"Actual cart quantity: {updated_item['quantity']}"
        )

    finally:
        delete_test_user(user["email"])