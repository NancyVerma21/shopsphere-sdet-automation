import os
import uuid

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


def create_inactive_user():
    unique_id = uuid.uuid4().hex[:10]

    email = f"inactive_test_{unique_id}@example.com"
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
                "Inactive",
                f"Test{unique_id}",
                email,
                password_hash,
                "customer",
                0,
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


def test_inactive_user_cannot_login(page: Page):
    user = create_inactive_user()

    try:
        login_page = LoginPage(page)

        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        login_page.login(
            email=user["email"],
            password=user["password"],
        )

        page.wait_for_load_state("networkidle")

        # An inactive account must not be authenticated.
        #
        # The current AUT redirects this account to the home page,
        # which indicates that login was accepted.
        assert "/login" in page.url, (
            "Inactive account was authenticated. "
            f"Unexpected URL after login: {page.url}"
        )

        expect(
            page.get_by_text(
                "Invalid email or password.",
                exact=True,
            )
        ).to_be_visible()

        # Additional authorization check:
        # an inactive account must not be able to access
        # a protected customer page.
        page.goto(f"{BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        assert "/login" in page.url, (
            "Inactive account can access protected Orders page. "
            f"Unexpected URL: {page.url}"
        )

    finally:
        delete_test_user(user["email"])