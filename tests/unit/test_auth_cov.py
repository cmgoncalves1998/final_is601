from datetime import timedelta
import asyncio
import threading
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.auth import jwt as jwt_mod
from app.auth import redis as redis_mod
from app.schemas.token import TokenType
from app.schemas.user import PasswordUpdate, UserCreate


def wait(coro):
    box = {}

    def run():
        try:
            box["val"] = asyncio.run(coro)
        except BaseException as exc:
            box["err"] = exc

    th = threading.Thread(target=run)
    th.start()
    th.join()
    if "err" in box:
        raise box["err"]
    return box.get("val")


def valid_user(**overrides):
    data = {
        "first_name": "Valid",
        "last_name": "User",
        "email": "valid@example.com",
        "username": "validuser",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }
    data.update(overrides)
    return data


def test_usr_schema_branches():
    with pytest.raises(ValueError):
        UserCreate(**valid_user(confirm_password="OtherPass123!"))
    for pwd in ["short", "securepass123!", "SECUREPASS123!", "SecurePass!", "SecurePass123"]:
        with pytest.raises(ValueError):
            UserCreate(**valid_user(password=pwd, confirm_password=pwd))

    with pytest.raises(ValueError):
        PasswordUpdate(
            current_password="OldPass123!",
            new_password="NewPass123!",
            confirm_new_password="Mismatch123!",
        )
    with pytest.raises(ValueError):
        PasswordUpdate(
            current_password="SamePass123!",
            new_password="SamePass123!",
            confirm_new_password="SamePass123!",
        )
    assert PasswordUpdate(
        current_password="OldPass123!",
        new_password="NewPass123!",
        confirm_new_password="NewPass123!",
    )


def test_make_decode_tok(monkeypatch):
    async def not_blocked(_jti):
        return False

    monkeypatch.setattr(jwt_mod, "is_blacklisted", not_blocked)
    token = jwt_mod.create_token(uuid4(), TokenType.ACCESS, timedelta(minutes=1))
    payload = wait(jwt_mod.decode_token(token, TokenType.ACCESS))

    assert payload["type"] == TokenType.ACCESS.value


def test_decode_tok_errors(monkeypatch):
    async def not_blocked(_jti):
        return False

    async def blocked(_jti):
        return True

    monkeypatch.setattr(jwt_mod, "is_blacklisted", not_blocked)
    refresh = jwt_mod.create_token("user-id", TokenType.REFRESH, timedelta(minutes=1))
    with pytest.raises(HTTPException) as exc:
        wait(jwt_mod.decode_token(refresh, TokenType.ACCESS))
    assert exc.value.status_code == 401

    access = jwt_mod.create_token("user-id", TokenType.ACCESS, timedelta(minutes=1))
    monkeypatch.setattr(jwt_mod, "is_blacklisted", blocked)
    with pytest.raises(HTTPException) as exc:
        wait(jwt_mod.decode_token(access, TokenType.ACCESS))
    assert exc.value.status_code == 401

    expired = jwt_mod.create_token("user-id", TokenType.ACCESS, timedelta(seconds=-1))
    with pytest.raises(HTTPException) as exc:
        wait(jwt_mod.decode_token(expired, TokenType.ACCESS))
    assert exc.value.status_code == 401

    with pytest.raises(HTTPException) as exc:
        wait(jwt_mod.decode_token("bad-token", TokenType.ACCESS))
    assert exc.value.status_code == 401


def test_cur_usr_success(monkeypatch):
    u = SimpleNamespace(id=uuid4(), is_active=True)

    async def dec(_token, _kind):
        return {"sub": str(u.id)}

    class Q:
        def filter(self, *_args):
            return self

        def first(self):
            return u

    db = SimpleNamespace(query=lambda _model: Q())
    monkeypatch.setattr(jwt_mod, "decode_token", dec)

    assert wait(jwt_mod.get_current_user(token="tok", db=db)) is u


def test_redis_helpers(monkeypatch):
    monkeypatch.setattr(redis_mod, "aioredis", None)
    if hasattr(redis_mod.get_redis, "redis"):
        delattr(redis_mod.get_redis, "redis")
    assert wait(redis_mod.get_redis()) is None
    assert wait(redis_mod.add_to_blacklist("j", 1)) is None
    assert wait(redis_mod.is_blacklisted("j")) is False

    class FakeRedis:
        async def set(self, *_args, **_kwargs):
            return None

        async def exists(self, _key):
            return 1

    class FakeAioredis:
        async def from_url(self, _url):
            return FakeRedis()

    monkeypatch.setattr(redis_mod, "aioredis", FakeAioredis())
    if hasattr(redis_mod.get_redis, "redis"):
        delattr(redis_mod.get_redis, "redis")
    assert wait(redis_mod.get_redis()) is not None
    assert wait(redis_mod.add_to_blacklist("j", 1)) is None
    assert wait(redis_mod.is_blacklisted("j")) is True

    class BadAioredis:
        async def from_url(self, _url):
            raise RuntimeError("no redis")

    monkeypatch.setattr(redis_mod, "aioredis", BadAioredis())
    if hasattr(redis_mod.get_redis, "redis"):
        delattr(redis_mod.get_redis, "redis")
    assert wait(redis_mod.get_redis()) is None
