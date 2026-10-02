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

    email = f"api_logout_{unique_id}@example.com"
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
                f"Logout{unique_id}",
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


def test_logout_api_invalidates_session(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        # Login and retain the API session cookie.
        login_response = api_context.post(
            "/login",
            form={
                "email": user["email"],
                "password": user["password"],
            },
            max_redirects=0,
        )

        assert login_response.status == 302

        # Confirm authenticated access before logout.
        orders_before_logout = api_context.get(
            "/orders",
            max_redirects=0,
        )

        assert orders_before_logout.status == 200

        # Perform logout.
        logout_response = api_context.get(
            "/logout",
            max_redirects=0,
        )

        assert logout_response.status == 302

        logout_location = logout_response.headers.get(
            "location",
            "",
        )

        assert "/login" in logout_location

        # After logout, protected access must be denied.
        orders_after_logout = api_context.get(
            "/orders",
            max_redirects=0,
        )

        # Expected secure behavior:
        # the session should be invalidated and the user should
        # be redirected to /login.
        #
        # The current AUT is expected to fail this assertion
        # because /logout does not clear the session.

        assert orders_after_logout.status in (301, 302), (
            "Authenticated session remained active after logout. "
            f"Unexpected HTTP status: "
            f"{orders_after_logout.status}"
        )

        location_after_logout = (
            orders_after_logout.headers.get(
                "location",
                "",
            )
        )

        assert "/login" in location_after_logout

    finally:
        delete_test_user(user["email"])