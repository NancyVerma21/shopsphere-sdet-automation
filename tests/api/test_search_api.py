import os

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


def get_search_candidate():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                sku,
                name,
                description,
                is_active
            FROM products
            WHERE is_active = TRUE
            ORDER BY id ASC
            """
        )

        products = cursor.fetchall()

        for product in products:
            name_words = [
                word.strip(".,-_/()[]")
                for word in product["name"].split()
                if len(word.strip(".,-_/()[]")) >= 4
            ]

            for word in name_words:
                word_lower = word.lower()

                description = (
                    product["description"] or ""
                ).lower()

                sku = (
                    product["sku"] or ""
                ).lower()

                if (
                    word_lower not in description
                    and word_lower not in sku
                ):
                    return {
                        "sku": product["sku"],
                        "name": product["name"],
                        "search_term": word,
                    }

        return None

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


def test_search_by_product_name_returns_matching_product(
    api_context: APIRequestContext,
):
    candidate = get_search_candidate()

    assert candidate is not None, (
        "Could not find an active product with a name term "
        "that is absent from its description and SKU."
    )

    response = api_context.get(
        "/products",
        params={
            "q": candidate["search_term"],
        },
    )

    assert response.status == 200

    body = response.text()

    # Expected behavior:
    # searching with a term from the product name should
    # return the matching product.
    #
    # The current AUT is expected to fail because its SQL
    # search condition checks only description and SKU,
    # not product name.

    assert candidate["name"] in body, (
        "Product-name search did not return the matching product. "
        f"Search term: {candidate['search_term']!r}; "
        f"Expected product: {candidate['name']!r}"
    )


def test_search_by_sku_returns_matching_product(
    api_context: APIRequestContext,
):
    candidate = get_search_candidate()

    assert candidate is not None

    response = api_context.get(
        "/products",
        params={
            "q": candidate["sku"],
        },
    )

    assert response.status == 200

    body = response.text()

    assert candidate["name"] in body, (
        "SKU search did not return the matching product. "
        f"SKU: {candidate['sku']!r}; "
        f"Expected product: {candidate['name']!r}"
    )