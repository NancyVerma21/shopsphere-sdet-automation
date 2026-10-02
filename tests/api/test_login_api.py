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


def create_test_user(role="customer", is_active=1):
    unique_id = uuid.uuid4().hex[:10]

    email = f"api_login_{unique_id}@example.com"
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
                f"Login{unique_id}",
                email,
                password_hash,
                role,
                is_active,
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


def test_login_api_with_valid_credentials(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        response = api_context.post(
            "/login",
            form={
                "email": user["email"],
                "password": user["password"],
            },
            max_redirects=0,
        )

        assert response.status == 302

        location = response.headers.get(
            "location",
            "",
        )

        assert location == "/"

        set_cookie = response.headers.get(
            "set-cookie",
            "",
        )

        assert "session=" in set_cookie

    finally:
        delete_test_user(user["email"])


def test_login_api_rejects_invalid_password(
    api_context: APIRequestContext,
):
    user = create_test_user()

    try:
        response = api_context.post(
            "/login",
            form={
                "email": user["email"],
                "password": "WrongPassword@123",
            },
        )

        assert response.status == 200

        body = response.text()

        assert (
            "Invalid email or password."
            in body
        )

    finally:
        delete_test_user(user["email"])


def test_login_api_rejects_unknown_user(
    api_context: APIRequestContext,
):
    email = f"unknown_{uuid.uuid4().hex[:12]}@example.com"

    response = api_context.post(
        "/login",
        form={
            "email": email,
            "password": "TestPassword@123",
        },
    )

    assert response.status == 200

    body = response.text()

    assert (
        "Invalid email or password."
        in body
    )


def test_login_api_rejects_missing_credentials(
    api_context: APIRequestContext,
):
    response = api_context.post(
        "/login",
        form={
            "email": "",
            "password": "",
        },
    )

    assert response.status == 200

    body = response.text()

    assert (
        "Email and password are required."
        in body
    )


def test_login_api_rejects_inactive_user(
    api_context: APIRequestContext,
):
    user = create_test_user(
        role="customer",
        is_active=0,
    )

    try:
        response = api_context.post(
            "/login",
            form={
                "email": user["email"],
                "password": user["password"],
            },
            max_redirects=0,
        )

        # Expected secure behavior:
        # inactive users should remain on the login page.
        #
        # The current AUT is expected to fail this assertion
        # because it does not check is_active before creating
        # the session.

        assert response.status == 200, (
            "Inactive user was authenticated by the API. "
            f"Unexpected HTTP status: {response.status}"
        )

        body = response.text()

        assert (
            "Invalid email or password."
            in body
        )

    finally:
        delete_test_user(user["email"])