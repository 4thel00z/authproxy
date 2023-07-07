import logging
from datetime import timedelta
from typing import Annotated

from edgedb import AsyncIOClient
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from db import create_tenant, create_user, create_role, GetUserByUsernameResult
from libauthproxy import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRY,
    HOST,
    PORT,
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    get_current_user,
    OAUTH2,
)
from libauthproxy.models import CreateUser, CreateRole, Token, CreateTenant
from libauthproxy.utils import generate_basic_auth, flatten


def register_routes(app: FastAPI, db: AsyncIOClient, **kwargs):
    L = logging.getLogger(__name__)
    L.setLevel(logging.DEBUG)
    secret_key = kwargs.get("secret_key", SECRET_KEY)
    jwt_algorithm = kwargs.get("jwt_algorithm", JWT_ALGORITHM)
    access_token_expiry = kwargs.get("access_token_expiry", ACCESS_TOKEN_EXPIRY)
    admin_user = kwargs.get("admin_username", ADMIN_USERNAME)
    admin_password = kwargs.get("admin_password", ADMIN_PASSWORD)
    host = kwargs.get("host", HOST)
    port = kwargs.get("port", PORT)
    get_current_username = generate_basic_auth(admin_user, admin_password)

    if not all((secret_key, jwt_algorithm, access_token_expiry, admin_user, admin_password)):
        raise EnvironmentError("$SECRET_KEY, $JWT_ALGORITHM, $ACCESS_TOKEN_EXPIRY, "
                               "$ADMIN_USERNAME and $ADMIN_PASSWORD have to be set")

    L.info(f"Registering POST http://{host}:{port}/roles")

    @app.post("/tenants")
    async def handle_create_tenants(
            _: Annotated[str, Depends(get_current_username)],
            tenant: CreateTenant
    ):
        return await create_tenant(db, **tenant.dict())

    L.info(f"Registering POST http://{host}:{port}/users")

    @app.post("/users")
    async def handle_create_users(
            _: Annotated[str, Depends(get_current_username)],
            user: CreateUser,
    ):
        return await create_user(db, **user.dict())

    L.info(f"Registering POST http://{host}:{port}/roles")

    @app.post("/roles")
    async def handle_create_roles(
            _: Annotated[str, Depends(get_current_username)],
            role: CreateRole,
    ):
        return await create_role(db, **role.dict())

    L.info(f"Registering POST http://{host}:{port}/tokens")

    @app.post("/tokens", response_model=Token)
    async def handle_create_token(
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
            tenant: Annotated[str, Form()]
    ):
        user = await authenticate_user(db, form_data.username, form_data.password, tenant)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(seconds=access_token_expiry)
        access_token = create_access_token(
            secret_key,
            jwt_algorithm,
            data={
                "sub": user.username,
                "tenant": user.tenant.name,
                "email": user.email,
                "disabled": user.disabled,
                "scopes": flatten([role.scopes for role in user.roles])
            },
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    L.info(f"Registering POST http://{host}:{port}/users/me")

    @app.get("/users/me/", response_model=GetUserByUsernameResult)
    async def handle_read_users_me(
            req: Request,
    ):
        return get_current_active_user(await get_current_user(db, secret_key, jwt_algorithm, await OAUTH2(req)))
