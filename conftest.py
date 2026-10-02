import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent
USERS_FILE = PROJECT_ROOT / "data" / "users.json"
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"


KNOWN_AUT_DEFECTS = {
    "test_cart_api_rejects_quantity_above_stock": "BUG-002",
    "test_search_by_product_name_returns_matching_product": "BUG-004",
    "test_exact_1000_subtotal_gets_free_shipping": "BUG-005",
    "test_cancel_button_hidden_for_cancelled_order": "BUG-006",
    "test_inactive_user_cannot_login": "BUG-007",
    "test_login_api_rejects_inactive_user": "BUG-007",
    "test_logout_invalidates_authenticated_session": "BUG-008",
    "test_logout_api_invalidates_session": "BUG-008",
    "test_customer_cannot_access_admin_dashboard": "BUG-009",
    "test_customer_cannot_access_admin_api": "BUG-009",
    "test_register_api_rejects_4_character_password": "BUG-010",
    "test_user_cannot_view_another_users_order": "BUG-012",
    "test_customer_cannot_view_another_users_order": "BUG-012",
    "test_customer_cannot_view_another_users_order_confirmation": "BUG-013",
    "test_customer_cannot_cancel_another_users_order": "BUG-014",
    "test_cancelled_order_cannot_be_cancelled_again": "BUG-015",
    "test_cancel_button_hidden_for_shipped_order": "BUG-020",
}


def get_normalized_test_name(item):
    return item.name.split("[", 1)[0]


def get_bug_id_for_test(item):
    test_name = get_normalized_test_name(item)

    if test_name in KNOWN_AUT_DEFECTS:
        return KNOWN_AUT_DEFECTS[test_name]

    file_name = item.path.name

    if file_name == "test_products.py":
        if (
            "sort" in test_name.lower()
            and "price" in test_name.lower()
        ):
            return "BUG-003"

    if file_name == "test_cart.py":
        name = test_name.lower()

        if (
            "quantity" in name
            and "stock" in name
            and (
                "exceed" in name
                or "greater" in name
                or "above" in name
            )
        ):
            return "BUG-002"

    if file_name == "test_checkout.py":
        name = test_name.lower()

        if (
            "successful_card_payment_creates_order" in name
            or "successful_checkout" in name
        ):
            return "BUG-019"

    return None


@pytest.fixture
def users():
    with open(
        USERS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


@pytest.fixture
def app_ready():
    return True


def pytest_collection_modifyitems(config, items):
    for item in items:
        bug_id = get_bug_id_for_test(item)

        if not bug_id:
            continue

        item.add_marker(
            pytest.mark.xfail(
                strict=True,
                reason=(
                    f"Known ShopSphere AUT defect: "
                    f"{bug_id}"
                ),
            )
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if not report.failed and not getattr(
        report,
        "wasxfail",
        False,
    ):
        return

    page = item.funcargs.get("page")

    if not page:
        return

    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_test_name = (
        item.nodeid
        .replace("\\", "_")
        .replace("/", "_")
        .replace("::", "__")
        .replace("[", "_")
        .replace("]", "_")
        .replace(":", "_")
    )

    screenshot_path = (
        SCREENSHOT_DIR
        / f"{safe_test_name}.png"
    )

    try:
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )
    except Exception:
        pass