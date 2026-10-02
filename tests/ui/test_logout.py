import os
import uuid

import mysql.connector
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from werkzeug.security import generate_password_hash

from pages.login_page import LoginPage
from pages.orders_page import OrdersPage
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

    email = f"logout_test_{unique_id}@example.com"
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
                "Logout",
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


def login_user(page: Page, email: str, password: str):
    login_page = LoginPage(page)

    page.goto(f"{BASE_URL}/login")

    login_page.login(
        email=email,
        password=password,
    )

    page.wait_for_load_state("networkidle")


def test_logout_invalidates_authenticated_session(page: Page):
    user = create_test_user()

    try:
        login_user(
            page,
            user["email"],
            user["password"],
        )

        # Confirm the user is authenticated before logout.
        page.goto(f"{BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        assert page.url == f"{BASE_URL}/orders"

        # Verify Logout link is displayed.
        logout_link = page.get_by_role(
            "link",
            name="Logout",
            exact=True,
        )

        expect(logout_link).to_be_visible()

        # Perform logout.
        logout_link.click()
        page.wait_for_load_state("networkidle")

        # Logout should redirect to login page.
        assert "/login" in page.url

        # After logout, attempt to access a protected page again.
        page.goto(f"{BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        # Security expectation:
        # an authenticated session must no longer provide
        # access to the protected Orders page.
        assert "/login" in page.url

        expect(
            page.get_by_role(
                "heading",
                name="Welcome back",
                exact=True,
            )
        ).to_be_visible()

    finally:
        delete_test_user(user["email"])