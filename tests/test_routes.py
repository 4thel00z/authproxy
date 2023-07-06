import httpx
import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from authproxy import init_app
from db import GetUserByEmailResult
from libauthproxy import get_current_user


class DBMock:
    def __init__(self, *, query_result=None, query_single_result=None):
        self.query_single_result = query_single_result
        self.query_result = query_result

    async def query_single(self, *args, **kwargs):
        return self.query_single_result

    async def query(self, *args, **kwargs):
        return self.query_result


@pytest.mark.asyncio
async def test_create_token__user_is_present_hash_matches():
    expected_user = GetUserByEmailResult(
        id="fake-news",
        username="buffy",
        email="buffy@buff.com",
        first_name="not-needed",
        last_name="not-needed",
        # obtained by running `poetry run python3 scripts/hash_password.py password`
        password_hash="$2b$12$lYWCG4Gu9mRViAKBjKW0zudnt9eXeQb0SHEIfJ4fSz3JJ2P1Zdyea",
        disabled=False,
    )
    mock = DBMock(query_single_result=expected_user)

    secret = "habins"
    algorithm = "HS256"
    app = init_app(db=mock, secret_key=secret, jwt_algorithm=algorithm)
    client = TestClient(app)
    res: httpx.Response = client.post("/token", data={
        # db always returns, so this is not important for now
        "username": "buffy",
        "password": "password"
    })
    assert res.status_code != 401
    res_body = res.json()
    token = res_body.get("access_token")
    assert token
    assert res_body.get("token_type") == "bearer"
    try:
        user = await get_current_user(mock, secret=secret, algorithm=algorithm, token=token)
        assert user.username == expected_user.username
        assert user.password_hash == expected_user.password_hash
    except HTTPException as err:
        assert False, str(err)


@pytest.mark.asyncio
async def test_create_token__user_is_present_wrong_hash():
    mock = DBMock(query_single_result=GetUserByEmailResult(
        id="fake-news",
        username="buffy",
        email="buffy@buff.com",
        first_name="not-needed",
        last_name="not-needed",
        # obtained by running `poetry run python3 scripts/hash_password.py BIGMOE`
        password_hash="$2b$12$hz/PMvvmutOVPgZol3.0F.nZboj6O1Fklv0LGWS4xE3UwH1HyVwge",
        disabled=False,
    ))

    app = init_app(db=mock, secret_key="habins")
    client = TestClient(app)
    res: httpx.Response = client.post("/token", data={
        # db always returns, so this is not important for now
        "username": "some-user",
        "password": "password"
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_create_token__no_user():
    mock = DBMock(query_single_result=None)

    app = init_app(db=mock, secret_key="habins")
    client = TestClient(app)
    res: httpx.Response = client.post("/token", data={
        # db always returns, so this is not important for now
        "username": "some-user",
        "password": "password"
    })
    assert res.status_code == 401
