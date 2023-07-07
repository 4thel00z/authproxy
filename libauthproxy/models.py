from pydantic import BaseModel


class CreateTenant(BaseModel):
    tenant: str


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password_hash: str
    tenant_name: str
    roles: str


class CreateRole(BaseModel):
    tenant: str
    scopes: list[str]
    tenant_name: str


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
