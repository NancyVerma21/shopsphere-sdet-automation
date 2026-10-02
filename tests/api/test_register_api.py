import os
import uuid

import mysql.connector
import pytest
from dotenv import load_dotenv
from playwright.sync_api import APIRequestContext, Playwright

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


def generate_unique_email():
    return f"api_register_{uuid.uuid4().hex[:12]}@example.com"


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


def get_user_by_email(email: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                first_name,
                last_name,
                email,
                password_hash,
                role,
                is_active
            FROM users
            WHERE email = %s
            """,
            (email,),
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


def test_register_api_creates_customer(
    api_context: APIRequestContext,
):
    email = generate_unique_email()

    try:
        response = api_context.post(
            "/register",
            form={
                "first_name": "API",
                "last_name": "Tester",
                "email": email,
                "password": "TestPassword@123",
                "confirm_password": "TestPassword@123",
            },
            max_redirects=0,
        )

        assert response.status == 302

        location = response.headers.get(
            "location",
            "",
        )

        assert "/login" in location

        user = get_user_by_email(email)

        assert user is not None
        assert user["first_name"] == "API"
        assert user["last_name"] == "Tester"
        assert user["email"] == email
        assert user["role"] == "customer"
        assert user["is_active"] == 1

        assert user["password_hash"] != (
            "TestPassword@123"
        )

    finally:
        delete_test_user(email)


def test_register_api_rejects_4_character_password(
    api_context: APIRequestContext,
):
    email = generate_unique_email()

    try:
        response = api_context.post(
            "/register",
            form={
                "first_name": "API",
                "last_name": "Boundary",
                "email": email,
                "password": "Ab12",
                "confirm_password": "Ab12",
            },
            max_redirects=0,
        )

        # Canonical BUG-010 expectation:
        # passwords with only 4-7 characters should be rejected.
        #
        # The current AUT accepts the 4-character password
        # and creates the account. Therefore this assertion
        # intentionally fails when BUG-010 is present.

        user = get_user_by_email(email)

        assert user is None, (
            "BUG-010 confirmed: a 4-character password "
            "was accepted and the user account was created."
        )

        assert response.status == 200

    finally:
        delete_test_user(email)


def test_register_api_rejects_password_mismatch(
    api_context: APIRequestContext,
):
    email = generate_unique_email()

    try:
        response = api_context.post(
            "/register",
            form={
                "first_name": "API",
                "last_name": "Tester",
                "email": email,
                "password": "TestPassword@123",
                "confirm_password": "DifferentPassword@123",
            },
        )

        assert response.status == 200

        body = response.text()

        assert (
            "Password and confirm password do not match."
            in body
        )

        assert get_user_by_email(email) is None

    finally:
        delete_test_user(email)


def test_register_api_rejects_duplicate_email(
    api_context: APIRequestContext,
):
    email = generate_unique_email()

    try:
        first_response = api_context.post(
            "/register",
            form={
                "first_name": "First",
                "last_name": "User",
                "email": email,
                "password": "TestPassword@123",
                "confirm_password": "TestPassword@123",
            },
            max_redirects=0,
        )

        assert first_response.status == 302

        first_location = first_response.headers.get(
            "location",
            "",
        )

        assert "/login" in first_location

        second_response = api_context.post(
            "/register",
            form={
                "first_name": "Second",
                "last_name": "User",
                "email": email,
                "password": "AnotherPassword@123",
                "confirm_password": "AnotherPassword@123",
            },
        )

        assert second_response.status == 200

        body = second_response.text()

        assert (
            "An account with this email already exists."
            in body
        )

        user = get_user_by_email(email)

        assert user is not None
        assert user["first_name"] == "First"
        assert user["last_name"] == "User"

    finally:
        delete_test_user(email)