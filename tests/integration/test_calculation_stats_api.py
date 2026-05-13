from uuid import uuid4

import pytest
import requests


@pytest.fixture
def base_url(fastapi_server: str) -> str:
    return fastapi_server.rstrip("/")


def reg_login(base_url: str, suffix: str) -> dict:
    usr = {
        "first_name": "St",
        "last_name": "Usr",
        "email": f"st.usr.{suffix}@example.com",
        "username": f"st_usr_{suffix}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }
    reg_r = requests.post(f"{base_url}/auth/register", json=usr)
    assert reg_r.status_code == 201, reg_r.text

    log_r = requests.post(
        f"{base_url}/auth/login",
        json={"username": usr["username"], "password": usr["password"]},
    )
    assert log_r.status_code == 200, log_r.text
    return log_r.json()


def test_calc_stat_req_auth(base_url: str):
    res = requests.get(f"{base_url}/calculations/stats")

    assert res.status_code == 401


def test_calc_stat_reports_user_hist(base_url: str):
    suffix = uuid4().hex
    tok = reg_login(base_url, suffix)
    h = {"Authorization": f"Bearer {tok['access_token']}"}

    empty_r = requests.get(f"{base_url}/calculations/stats", headers=h)
    assert empty_r.status_code == 200, empty_r.text
    empty_s = empty_r.json()
    assert empty_s["total_calculations"] == 0
    assert empty_s["average_inputs_per_calculation"] == 0.0
    assert empty_s["average_result"] is None
    assert empty_s["most_used_operation"] is None

    calcs = [
        {"type": "addition", "inputs": [1, 2, 3]},
        {"type": "division", "inputs": [20, 2]},
    ]
    for p in calcs:
        create_r = requests.post(
            f"{base_url}/calculations",
            json=p,
            headers=h,
        )
        assert create_r.status_code == 201, create_r.text

    stats_r = requests.get(f"{base_url}/calculations/stats", headers=h)
    assert stats_r.status_code == 200, stats_r.text
    s = stats_r.json()

    assert s["total_calculations"] == 2
    assert s["average_inputs_per_calculation"] == 2.5
    assert s["average_result"] == 8.0
    assert s["operation_counts"]["addition"] == 1
    assert s["operation_counts"]["division"] == 1
    assert s["operation_counts"]["subtraction"] == 0
    assert s["operation_counts"]["multiplication"] == 0
    assert s["most_used_operation"] == "addition"
    assert s["latest_calculation_at"] is not None


def test_calc_stat_user_isolation(base_url: str):
    first_suf = uuid4().hex
    sec_suf = uuid4().hex
    first_u = reg_login(base_url, first_suf)
    sec_u = reg_login(base_url, sec_suf)

    first_h = {"Authorization": f"Bearer {first_u['access_token']}"}
    sec_h = {"Authorization": f"Bearer {sec_u['access_token']}"}

    create_r = requests.post(
        f"{base_url}/calculations",
        json={"type": "multiplication", "inputs": [3, 4]},
        headers=first_h,
    )
    assert create_r.status_code == 201, create_r.text

    sec_stats_r = requests.get(
        f"{base_url}/calculations/stats",
        headers=sec_h,
    )
    assert sec_stats_r.status_code == 200, sec_stats_r.text
    assert sec_stats_r.json()["total_calculations"] == 0
