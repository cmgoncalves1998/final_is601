from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import main
from app.models.calculation import Calculation


class Db:
    def __init__(self, rows=None, first=None):
        self.rows = rows or []
        self.first_row = first
        self.deleted = None
        self.did_commit = False
        self.did_rollback = False

    def add(self, obj):
        now = datetime.utcnow()
        obj.id = getattr(obj, "id", None) or uuid4()
        obj.created_at = getattr(obj, "created_at", None) or now
        obj.updated_at = getattr(obj, "updated_at", None) or now

    def commit(self):
        self.did_commit = True

    def refresh(self, obj):
        return None

    def rollback(self):
        self.did_rollback = True

    def query(self, model):
        return self

    def filter(self, *args):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.first_row

    def delete(self, obj):
        self.deleted = obj


def user(**overrides):
    data = {
        "id": uuid4(),
        "username": "usr",
        "email": "usr@example.com",
        "first_name": "U",
        "last_name": "R",
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def calc(**overrides):
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "addition",
        "inputs": [1, 2],
        "result": 3,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    data.update(overrides)
    c = SimpleNamespace(**data)
    c.get_result = lambda: sum(c.inputs)
    return c


@pytest.fixture
def client():
    main.app.dependency_overrides.clear()
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


def use_db(db):
    main.app.dependency_overrides[main.get_db] = lambda: db


def use_user(u):
    main.app.dependency_overrides[main.get_current_active_user] = lambda: u


def test_pages_health(client):
    for path in ["/", "/login", "/register", "/dashboard", f"/dashboard/view/{uuid4()}", f"/dashboard/edit/{uuid4()}"]:
        assert client.get(path).status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_reg_ok_and_bad(client, monkeypatch):
    db = Db()
    use_db(db)
    u = user(username="newusr")
    monkeypatch.setattr(main.User, "register", lambda _db, _data: u)

    payload = {
        "first_name": "New",
        "last_name": "Usr",
        "email": "new@example.com",
        "username": "newusr",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 201
    assert db.did_commit is True

    monkeypatch.setattr(main.User, "register", lambda _db, _data: (_ for _ in ()).throw(ValueError("dup")))
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 400
    assert db.did_rollback is True


def test_login_json_paths(client, monkeypatch):
    db = Db()
    use_db(db)
    u = user()
    auth = {
        "access_token": "a",
        "refresh_token": "r",
        "expires_at": datetime.utcnow(),
        "user": u,
    }
    monkeypatch.setattr(main.User, "authenticate", lambda *_args: auth)

    res = client.post("/auth/login", json={"username": "usr", "password": "SecurePass123!"})
    assert res.status_code == 200
    assert res.json()["username"] == "usr"
    assert db.did_commit is True

    monkeypatch.setattr(main.User, "authenticate", lambda *_args: None)
    res = client.post("/auth/login", json={"username": "usr", "password": "SecurePass123!"})
    assert res.status_code == 401


def test_login_form_paths(client, monkeypatch):
    use_db(Db())
    monkeypatch.setattr(main.User, "authenticate", lambda *_args: {"access_token": "tok"})

    res = client.post("/auth/token", data={"username": "usr", "password": "SecurePass123!"})
    assert res.status_code == 200
    assert res.json() == {"access_token": "tok", "token_type": "bearer"}

    monkeypatch.setattr(main.User, "authenticate", lambda *_args: None)
    res = client.post("/auth/token", data={"username": "usr", "password": "SecurePass123!"})
    assert res.status_code == 401


def test_calc_routes(client):
    u = user()
    c = calc(user_id=u.id)
    db = Db(rows=[c], first=c)
    use_db(db)
    use_user(u)

    res = client.post("/calculations", json={"type": "addition", "inputs": [1, 2]})
    assert res.status_code == 201
    created_id = res.json()["id"]

    assert client.get("/calculations").status_code == 200
    assert client.get("/calculations/stats").json()["total_calculations"] == 1
    assert client.get(f"/calculations/{created_id}").status_code == 200
    assert client.put(f"/calculations/{created_id}", json={"inputs": [3, 4]}).json()["result"] == 7
    assert client.delete(f"/calculations/{created_id}").status_code == 204
    assert db.deleted is c


def test_calc_route_errs(client, monkeypatch):
    u = user()
    db = Db()
    use_db(db)
    use_user(u)

    monkeypatch.setattr(Calculation, "create", lambda **_kwargs: (_ for _ in ()).throw(ValueError("bad op")))
    res = client.post("/calculations", json={"type": "addition", "inputs": [1, 2]})
    assert res.status_code == 400
    assert db.did_rollback is True

    for method, path in [
        ("get", "/calculations/not-a-uuid"),
        ("put", "/calculations/not-a-uuid"),
        ("delete", "/calculations/not-a-uuid"),
    ]:
        if method == "put":
            res = client.put(path, json={"inputs": [1, 2]})
        else:
            res = getattr(client, method)(path)
        assert res.status_code == 400

    missing = uuid4()
    assert client.get(f"/calculations/{missing}").status_code == 404
    assert client.put(f"/calculations/{missing}", json={"inputs": [1, 2]}).status_code == 404
    assert client.delete(f"/calculations/{missing}").status_code == 404
