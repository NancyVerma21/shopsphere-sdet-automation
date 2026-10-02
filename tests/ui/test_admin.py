import os
import uuid

import mysql.connector
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from werkzeug.security import generate_password_hash

from pages.admin_page import AdminPage
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


def create_test_user(role: str):
    unique_id = uuid.uuid4().hex[:10]

    email = f"admin_test_{role}_{unique_id}@example.com"
    password = "TestPassword@123"

    first_name = "Admin" if role == "admin" else "Customer"
    last_name = f"Test{unique_id}"

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
                first_name,
                last_name,
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
        "first_name": first_name,
        "last_name": last_name,
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


def test_admin_user_can_access_admin_dashboard(page: Page):
    admin_user = create_test_user("admin")

    try:
        login_user(
            page,
            admin_user["email"],
            admin_user["password"],
        )

        admin_page = AdminPage(page)
        admin_page.open()

        admin_page.assert_dashboard_visible()

        expect(
            page.get_by_text(
                "Role:",
                exact=False,
            )
        ).to_be_visible()

        assert "admin" in admin_page.get_role_text().lower()

    finally:
        delete_test_user(admin_user["email"])


def test_customer_cannot_access_admin_dashboard(page: Page):
    customer = create_test_user("customer")

    try:
        login_user(
            page,
            customer["email"],
            customer["password"],
        )

        admin_page = AdminPage(page)
        admin_page.open()

        # Security expectation:
        # a normal customer must not be allowed to access
        # the administrator dashboard.
        #
        # The current AUT is expected to fail this test
        # because the /admin route does not enforce a role check.

        expect(
            admin_page.page_heading
        ).not_to_be_visible()

        assert "/admin" not in page.url

    finally:
        delete_test_user(customer["email"])