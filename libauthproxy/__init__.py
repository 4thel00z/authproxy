from datetime import timedelta, datetime
from os import environ

from edgedb import AsyncIOClient
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status
from typing_extensions import Annotated

from db import get_user_by_username, GetUserByUsernameResult
from libauthproxy.utils import catch

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2 = OAuth2PasswordBearer(tokenUrl="token")

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = environ.get("SECRET_KEY")
JWT_ALGORITHM = environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRY = int(environ.get("ACCESS_TOKEN_EXPIRY", "3600"))
ADMIN_USERNAME = environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = environ.get("ADMIN_PASSWORD")
HOST = environ.get("HOST", "0.0.0.0")
PORT = int(environ.get("PORT", "1337"))


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return PWD_CONTEXT.hash(plain_password)


async def authenticate_user(db: AsyncIOClient, username: str, password: str,
                            tenant: str) -> bool | GetUserByUsernameResult:
    user = await get_user_by_username(db, username=username, tenant=tenant)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(secret: str, algorithm: str, data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt


async def get_current_user(
        db: AsyncIOClient,
        secret: str,
        algorithm: str,
        token: Annotated[str, Depends(OAUTH2)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    with catch(JWTError) as errs:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        username: str = payload.get("sub")
        tenant: str = payload.get("tenant")

        if not username or not tenant:
            raise credentials_exception

        user = await get_user_by_username(db, username=username, tenant=tenant)

        if user is None:
            raise credentials_exception

        return user

    if errs.err:
        raise credentials_exception


def get_current_active_user(
        current_user
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user
