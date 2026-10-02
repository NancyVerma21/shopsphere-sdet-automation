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


def create_test_user(role="customer"):
    unique_id = uuid.uuid4().hex[:10]

    email = f"api_auth_{role}_{unique_id}@example.com"
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
                f"Auth{unique_id}",
                email,
                password_hash,
                role,
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
            "DELETE FROM users WHERE email = %s",
            (email,),
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
    return api_context.post(
        "/login",
        form={
            "email": user["email"],
            "password": user["password"],
        },
        max_redirects=0,
    )


def test_admin_user_can_access_admin_api(
    api_context: APIRequestContext,
):
    admin_user = create_test_user("admin")

    try:
        login_response = login_user(
            api_context,
            admin_user,
        )

        assert login_response.status == 302

        admin_response = api_context.get(
            "/admin",
            max_redirects=0,
        )

        assert admin_response.status == 200

        body = admin_response.text()

        assert "Admin Dashboard" in body

        assert "Role:" in body

    finally:
        delete_test_user(admin_user["email"])


def test_customer_cannot_access_admin_api(
    api_context: APIRequestContext,
):
    customer = create_test_user("customer")

    try:
        login_response = login_user(
            api_context,
            customer,
        )

        assert login_response.status == 302

        admin_response = api_context.get(
            "/admin",
            max_redirects=0,
        )

        # Expected secure behavior:
        # a normal customer should be denied access to /admin.
        #
        # The current AUT is expected to fail this assertion
        # because the /admin route does not enforce the user's role.

        assert admin_response.status in (301, 302, 403), (
            "Customer was allowed to access the admin endpoint. "
            f"Unexpected HTTP status: {admin_response.status}"
        )

        if admin_response.status in (301, 302):
            location = admin_response.headers.get(
                "location",
                "",
            )

            assert "/login" in location or "/products" in location

    finally:
        delete_test_user(customer["email"])