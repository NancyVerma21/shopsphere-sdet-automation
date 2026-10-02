import pytest
from playwright.sync_api import APIRequestContext, Playwright

from utils.config import BASE_URL


@pytest.fixture
def api_context(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=BASE_URL
    )

    yield context

    context.dispose()


def test_database_health_api(api_context: APIRequestContext):
    response = api_context.get("/health/db")

    assert response.status == 200

    assert response.headers.get(
        "content-type",
        ""
    ).startswith("application/json")

    body = response.json()

    assert isinstance(body, dict)

    assert body["status"] == "healthy"

    assert body["database"] == "shopsphere"

    assert body["mysql_version"]

    assert isinstance(
        body["mysql_version"],
        str
    )