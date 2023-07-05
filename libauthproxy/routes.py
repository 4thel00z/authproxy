import logging
from datetime import timedelta
from typing import Annotated

from edgedb import AsyncIOClient
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from libauthproxy import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    Token,
    User,
    SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRY, get_current_user, OAUTH2,
)


def register_routes(app: FastAPI, db: AsyncIOClient):
    L = logging.getLogger(__name__)
    L.setLevel(logging.DEBUG)

    if not all((SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRY)):
        raise EnvironmentError("$SECRET_KEY, $JWT_ALGORITHM and ACCESS_TOKEN_EXPIRY have to be set")

    L.info("Registering POST http://0.0.0.0:1337/token")

    @app.post("/token", response_model=Token)
    async def handle_create_token(
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(seconds=ACCESS_TOKEN_EXPIRY)
        access_token = create_access_token(
            SECRET_KEY,
            JWT_ALGORITHM,
            data={
                "sub": user.username,
                "email": user.email,
                "disabled": user.disabled,
            },
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    L.info("Registering GET http://0.0.0.0:1337/users/me")

    @app.get("/users/me/", response_model=User)
    async def handle_read_users_me(
            req: Request,
    ):
        return get_current_active_user(await get_current_user(db, SECRET_KEY, JWT_ALGORITHM, await OAUTH2(req)))
