from datetime import timedelta
from uuid import UUID

import httpx
import pytest
from fastapi import HTTPException
from starlette import status
from starlette.testclient import TestClient

from authproxy import init_app
from db import GetUserByEmailResult, GetUserByEmailResultTenant
from libauthproxy import get_current_user, create_access_token


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
        id=UUID('12345678123456781234567812345678'),
        username="buffy",
        email="buffy@buff.com",
        first_name="not-needed",
        last_name="not-needed",
        # obtained by running `poetry run python3 scripts/hash_password.py password`
        password_hash="$2b$12$lYWCG4Gu9mRViAKBjKW0zudnt9eXeQb0SHEIfJ4fSz3JJ2P1Zdyea",
        disabled=False,
        roles=[],
        tenant=GetUserByEmailResultTenant(id=UUID('12345678123456781234567812345678'), name="aldi")
    )
    mock = DBMock(query_single_result=expected_user)

    secret = "habins"
    algorithm = "HS256"
    app = init_app(db=mock, secret_key=secret, jwt_algorithm=algorithm, admin_username="admin", admin_password="admin")
    client = TestClient(app)
    res: httpx.Response = client.post("/tokens", data={
        # db always returns, so this is not important for now
        "username": "buffy",
        "password": "password",
        "tenant": "aldi"
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
        id=UUID('12345678123456781234567812345678'),
        username="buffy",
        email="buffy@buff.com",
        first_name="not-needed",
        last_name="not-needed",
        # obtained by running `poetry run python3 scripts/hash_password.py BIGMOE`
        password_hash="$2b$12$hz/PMvvmutOVPgZol3.0F.nZboj6O1Fklv0LGWS4xE3UwH1HyVwge",
        disabled=False,
        roles=[],
        tenant=GetUserByEmailResultTenant(id=UUID('12345678123456781234567812345678'), name="aldi")
    ))

    app = init_app(db=mock, secret_key="habins", admin_username="admin", admin_password="admin")
    client = TestClient(app)
    res: httpx.Response = client.post("/tokens", data={
        # db always returns, so this is not important for now
        "username": "some-user",
        "password": "password",
        "tenant": "aldi"
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_create_token__no_user():
    mock = DBMock(query_single_result=None)

    app = init_app(db=mock, secret_key="habins", admin_username="admin", admin_password="admin")
    client = TestClient(app)
    res: httpx.Response = client.post("/tokens", data={
        # db always returns, so this is not important for now
        "username": "some-user",
        "password": "password",
        "tenant": "aldi"
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_users_me__happy_flow():
    mock = DBMock(query_single_result=GetUserByEmailResult(
        id=UUID('12345678123456781234567812345678'),
        username="buffy",
        email="buffy@buff.com",
        first_name="not-needed",
        last_name="not-needed",
        # obtained by running `poetry run python3 scripts/hash_password.py BIGMOE`
        password_hash="$2b$12$hz/PMvvmutOVPgZol3.0F.nZboj6O1Fklv0LGWS4xE3UwH1HyVwge",
        disabled=False,
        roles=[],
        tenant=GetUserByEmailResultTenant(id=UUID('12345678123456781234567812345678'), name="aldi")
    ))

    app = init_app(db=mock, secret_key="habins", admin_username="admin", admin_password="admin")
    client = TestClient(app)
    token = create_access_token("habins", "HS256", {"sub": "buffy", "tenant": "bigmoe"}, timedelta(days=1))
    res: httpx.Response = client.get("/users/me", headers={"authorization": f"Bearer {token}"})
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {
        'username': 'buffy',
        'email': 'buffy@buff.com',
        'first_name': 'not-needed',
        'last_name': 'not-needed',
        'disabled': False,
        'roles': [],
        'password_hash': '$2b$12$hz/PMvvmutOVPgZol3.0F.nZboj6O1Fklv0LGWS4xE3UwH1HyVwge',
        'id': '12345678-1234-5678-1234-567812345678',
        'tenant': {
            'id': '12345678-1234-5678-1234-567812345678',
            'name': 'aldi'
        },
    }

    @pytest.mark.asyncio
    async def test_users_me__no_user():
        mock = DBMock(query_single_result=None)
        app = init_app(db=mock, secret_key="habins", admin_username="admin", admin_password="admin")
        client = TestClient(app)
        token = create_access_token("habins", "HS256", {"sub": "bigmoe"}, timedelta(days=1))
        res: httpx.Response = client.get("/users/me", headers={"authorization": f"Bearer {token}"})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_users_me__invalid_token_sub_missing():
        mock = DBMock(query_single_result=GetUserByEmailResult(
            id=UUID('12345678123456781234567812345678'),
            username="buffy",
            email="buffy@buff.com",
            first_name="not-needed",
            last_name="not-needed",
            # obtained by running `poetry run python3 scripts/hash_password.py BIGMOE`
            password_hash="$2b$12$hz/PMvvmutOVPgZol3.0F.nZboj6O1Fklv0LGWS4xE3UwH1HyVwge",
            disabled=False,
            roles=[],
            tenant=GetUserByEmailResultTenant(id=UUID('12345678123456781234567812345678'), name="aldi")

        ))

        app = init_app(db=mock, secret_key="habins", admin_username="admin", admin_password="admin")
        client = TestClient(app)
        token = create_access_token("habins", "HS256", {}, timedelta(days=1))
        res: httpx.Response = client.get("/users/me", headers={"authorization": f"Bearer {token}"})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_users_me__invalid_token_sub_empty():
        mock = DBMock(query_single_result=GetUserByEmailResult(
            id=UUID('12345678123456781234567812345678'),
            username="buffy",
            email="buffy@buff.com",
            first_name="not-needed",
            last_name="not-needed",
            # obtained by running `poetry run python3 scripts/hash_password.py BIGMOE`
            password_hash="$2b$12$hz/PMvvmutOVPgZol3.0F.nZboj6O1Fklv0LGWS4xE3UwH1HyVwge",
            disabled=False,
            roles=[],
            tenant=GetUserByEmailResultTenant(id=UUID('12345678123456781234567812345678'), name="aldi")
        ))

        app = init_app(db=mock, secret_key="habins", admin_username="admin", admin_password="admin")
        client = TestClient(app)
        token = create_access_token("habins", "HS256", {"sub": ""}, timedelta(days=1))
        res: httpx.Response = client.get("/users/me", headers={"authorization": f"Bearer {token}"})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_users_me__user_disabled():
        mock = DBMock(query_single_result=GetUserByEmailResult(
            id=UUID('12345678123456781234567812345678'),
            username="buffy",
            email="buffy@buff.com",
            first_name="not-needed",
            last_name="not-needed",
            # obtained by running `poetry run python3 scripts/hash_password.py BIGMOE`
            password_hash="$2b$12$hz/PMvvmutOVPgZol3.0F.nZboj6O1Fklv0LGWS4xE3UwH1HyVwge",
            disabled=True,
            roles=[],
            tenant=GetUserByEmailResultTenant(id=UUID('12345678123456781234567812345678'), name="aldi"),
        ))

        app = init_app(db=mock, secret_key="habins", admin_username="admin", admin_password="admin")
        client = TestClient(app)
        token = create_access_token("habins", "HS256", {"sub": "buffy", "tenant": "aldi"}, timedelta(days=1))
        res: httpx.Response = client.get("/users/me", headers={"authorization": f"Bearer {token}"})
        assert res.status_code == status.HTTP_403_FORBIDDEN
