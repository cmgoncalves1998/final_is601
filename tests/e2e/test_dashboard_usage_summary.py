from uuid import uuid4

import pytest
import requests
from playwright.sync_api import Page, expect


@pytest.fixture
def base_url(fastapi_server: str) -> str:
    return fastapi_server.rstrip("/")


def reg_usr(base_url: str) -> dict:
    suf = uuid4().hex
    usr = {
        "first_name": "Br",
        "last_name": "St",
        "email": f"br.st.{suf}@example.com",
        "username": f"br_st_{suf}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }
    res = requests.post(f"{base_url}/auth/register", json=usr)
    assert res.status_code == 201, res.text
    return usr


def login_ui(page: Page, base_url: str, usr: dict) -> None:
    page.goto(f"{base_url}/login")
    page.fill("#username", usr["username"])
    page.fill("#password", usr["password"])
    page.click("button[type='submit']")
    page.wait_for_url("**/dashboard", timeout=7000)
    expect(page.locator("#statsPanel")).to_be_visible()


def mk_calc(page: Page, calc_type: str, nums: str) -> None:
    page.select_option("#calcType", calc_type)
    page.fill("#calcInputs", nums)
    page.click("#calculationForm button[type='submit']")


def test_dash_sum_updates(page: Page, base_url: str):
    usr = reg_usr(base_url)
    login_ui(page, base_url, usr)

    expect(page.locator("#statsTotal")).to_have_text("0")
    expect(page.locator("#statsAvgResult")).to_have_text("N/A")

    mk_calc(page, "addition", "5, 10")
    expect(page.locator("#statsTotal")).to_have_text("1")
    expect(page.locator("#statsAvgInputs")).to_have_text("2")
    expect(page.locator("#statsAvgResult")).to_have_text("15")
    expect(page.locator("#statsTopOperation")).to_have_text("Addition")

    mk_calc(page, "multiplication", "2, 3, 4")
    expect(page.locator("#statsTotal")).to_have_text("2")
    expect(page.locator("#statsAvgInputs")).to_have_text("2.5")
    expect(page.locator("#statsAvgResult")).to_have_text("19.5")
    expect(page.locator("#statsTopOperation")).to_have_text("Addition")
    expect(page.locator("#statsOperationBreakdown")).to_contain_text("Multiplication")
    expect(page.locator("#calculationsTable")).to_contain_text("24")


def test_dash_sum_bad_input(page: Page, base_url: str):
    usr = reg_usr(base_url)
    login_ui(page, base_url, usr)

    mk_calc(page, "addition", "only text")

    expect(page.locator("#errorMessage")).to_have_text(
        "Please enter at least two valid numbers, separated by commas"
    )
    expect(page.locator("#statsTotal")).to_have_text("0")
