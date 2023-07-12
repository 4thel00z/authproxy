from datetime import timedelta
from typing import Annotated

from edgedb import AsyncIOClient
from fastapi import Depends, FastAPI, HTTPException, status, Form, Path
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from db import (
    create_tenant,
    create_user,
    create_role,
    delete_role,
    delete_tenant,
    GetUserByUsernameResult, delete_user, read_role, list_roles, read_tenant, list_tenants, read_user, list_users,
)
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
    DEBUG,
)
from libauthproxy.models import CreateUser, CreateRole, Token, CreateTenant, DeleteRole, DeleteTenant, DeleteUser
from libauthproxy.utils import generate_basic_auth, flatten, L


def register_routes(app: FastAPI, db: AsyncIOClient, **kwargs):
    secret_key = kwargs.get("secret_key", SECRET_KEY)
    jwt_algorithm = kwargs.get("jwt_algorithm", JWT_ALGORITHM)
    access_token_expiry = kwargs.get("access_token_expiry", ACCESS_TOKEN_EXPIRY)
    admin_user = kwargs.get("admin_username", ADMIN_USERNAME)
    admin_password = kwargs.get("admin_password", ADMIN_PASSWORD)
    host = kwargs.get("host", HOST)
    port = kwargs.get("port", PORT)
    debug = kwargs.get("debug", DEBUG)
    get_current_username = generate_basic_auth(admin_user, admin_password)

    if not all((secret_key, jwt_algorithm, access_token_expiry, admin_user, admin_password)):
        raise EnvironmentError("$SECRET_KEY, $JWT_ALGORITHM, $ACCESS_TOKEN_EXPIRY, "
                               "$ADMIN_USERNAME and $ADMIN_PASSWORD have to be set")
    if debug:
        app.mount("/static", StaticFiles(directory="static"), name="static")

        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=app.title + " - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="/static/swagger-ui-bundle.js",
                swagger_css_url="/static/swagger-ui.css",
            )

        @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
        async def swagger_ui_redirect():
            return get_swagger_ui_oauth2_redirect_html()

        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title + " - ReDoc",
                redoc_js_url="/static/redoc.standalone.js",
            )

    L.info(f"Registering POST http://{host}:{port}/roles")

    @app.post("/tenants")
    async def handle_create_tenant(
            _: Annotated[str, Depends(get_current_username)],
            tenant: CreateTenant
    ):
        return await create_tenant(db, **tenant.dict())

    L.info(f"Registering POST http://{host}:{port}/users")

    @app.post("/users")
    async def handle_create_user(
            _: Annotated[str, Depends(get_current_username)],
            user: CreateUser,
    ):
        return await create_user(db, **user.dict())

    L.info(f"Registering POST http://{host}:{port}/roles")

    @app.post("/roles")
    async def handle_create_role(
            _: Annotated[str, Depends(get_current_username)],
            role: CreateRole,
    ):
        return await create_role(db, **role.dict())

    L.info(f"Registering DELETE http://{host}:{port}/roles")

    @app.delete("/roles")
    async def handle_delete_role(
            _: Annotated[str, Depends(get_current_username)],
            role: DeleteRole,
    ):
        return await delete_role(db, **role.dict())

    L.info(f"Registering DELETE http://{host}:{port}/tenants")

    @app.delete("/tenants")
    async def handle_delete_tenant(
            _: Annotated[str, Depends(get_current_username)],
            tenant: DeleteTenant,
    ):
        return await delete_tenant(db, **tenant.dict())

    L.info(f"Registering DELETE http://{host}:{port}/users")

    @app.delete("/users")
    async def handle_delete_user(
            _: Annotated[str, Depends(get_current_username)],
            user: DeleteUser,
    ):
        return await delete_user(db, **user.dict())

    L.info(f"Registering GET http://{host}:{port}/<tenant>/roles/<name>")

    @app.get("/tenants/{tenant}/roles/{name}")
    async def handle_read_role(
            _: Annotated[str, Depends(get_current_username)],
            tenant: Annotated[str, Path(title="The tenant under which the role is saved")],
            name: Annotated[str, Path(title="The name of the role")],
    ):
        return await read_role(db, name=name, tenant=tenant)

    L.info(f"Registering GET http://{host}:{port}/<tenant>/users")

    @app.get("/tenants/{tenant}/users")
    async def handle_list_users(
            _: Annotated[str, Depends(get_current_username)],
            tenant: Annotated[str, Path(title="The name of the tenant")],
    ):
        return await list_users(db, tenant=tenant)

    L.info(f"Registering GET http://{host}:{port}/<tenant>/users/<username>")

    @app.get("/tenants/{tenant}/users/{username}")
    async def handle_read_user(
            _: Annotated[str, Depends(get_current_username)],
            tenant: Annotated[str, Path(title="The name of the tenant")],
            username: Annotated[str, Path(title="The name of the user")],
    ):
        return await read_user(db, username=username, tenant=tenant)

    L.info(f"Registering GET http://{host}:{port}/tenants/<name>")

    @app.get("/tenants/{name}")
    async def handle_read_tenant(
            _: Annotated[str, Depends(get_current_username)],
            name: Annotated[str, Path(title="The name of the tenant")],
    ):
        return await read_tenant(db, tenant=name)

    L.info(f"Registering GET http://{host}:{port}/tenants")

    @app.get("/tenants")
    async def handle_list_tenants(
            _: Annotated[str, Depends(get_current_username)],
    ):
        return await list_tenants(db)

    L.info(f"Registering GET http://{host}:{port}/<tenant>/roles")

    @app.get("/tenants/{tenant}/roles")
    async def handle_list_roles(
            _: Annotated[str, Depends(get_current_username)],
            tenant: Annotated[str, Path(title="The tenant under which the role is saved")],
    ):
        return await list_roles(db, tenant=tenant)

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
