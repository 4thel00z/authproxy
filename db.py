# AUTOGENERATED FROM:
#     'queries/roles/create_role.edgeql'
#     'queries/tenants/create_tenant.edgeql'
#     'queries/users/create_user.edgeql'
#     'queries/roles/delete_role.edgeql'
#     'queries/tenants/delete_tenant.edgeql'
#     'queries/users/delete_user.edgeql'
#     'queries/users/get_user_by_email.edgeql'
#     'queries/users/get_user_by_username.edgeql'
#     'queries/roles/list_roles.edgeql'
#     'queries/tenants/list_tenants.edgeql'
#     'queries/users/list_users.edgeql'
#     'queries/roles/read_role.edgeql'
#     'queries/tenants/read_tenant.edgeql'
#     'queries/users/read_user.edgeql'
#     'queries/tenants/update_tenant.edgeql'
# WITH:
#     $ edgedb-py --file db.py


from __future__ import annotations
import dataclasses
import datetime
import edgedb
import uuid


class NoPydanticValidation:
    @classmethod
    def __get_validators__(cls):
        from pydantic.dataclasses import dataclass as pydantic_dataclass
        pydantic_dataclass(cls)
        cls.__pydantic_model__.__get_validators__ = lambda: []
        return []


@dataclasses.dataclass
class CreateRoleResult(NoPydanticValidation):
    id: uuid.UUID


@dataclasses.dataclass
class CreateTenantResult(NoPydanticValidation):
    id: uuid.UUID


@dataclasses.dataclass
class CreateUserResult(NoPydanticValidation):
    id: uuid.UUID


@dataclasses.dataclass
class GetUserByEmailResult(NoPydanticValidation):
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    password_hash: str
    disabled: bool
    roles: list[GetUserByEmailResultRolesItem]
    tenant: GetUserByEmailResultTenant


@dataclasses.dataclass
class GetUserByEmailResultRolesItem(NoPydanticValidation):
    id: uuid.UUID
    name: str
    scopes: list[str]


@dataclasses.dataclass
class GetUserByEmailResultTenant(NoPydanticValidation):
    id: uuid.UUID
    name: str


@dataclasses.dataclass
class GetUserByUsernameResult(NoPydanticValidation):
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    password_hash: str
    disabled: bool
    tenant: GetUserByEmailResultTenant
    roles: list[GetUserByEmailResultRolesItem]


@dataclasses.dataclass
class ListRolesResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    scopes: list[str]
    tenant: CreateTenantResult
    created_at: datetime.datetime


@dataclasses.dataclass
class ListTenantsResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    created_at: datetime.datetime


@dataclasses.dataclass
class ListUsersResult(NoPydanticValidation):
    id: uuid.UUID
    username: str
    created_at: datetime.datetime
    tenant: GetUserByEmailResultTenant
    first_name: str
    last_name: str
    email: str
    password_hash: str
    disabled: bool
    roles: list[ListUsersResultRolesItem]


@dataclasses.dataclass
class ListUsersResultRolesItem(NoPydanticValidation):
    id: uuid.UUID
    scopes: list[str]
    name: str


async def create_role(
    executor: edgedb.AsyncIOExecutor,
    *,
    name: str,
    scopes: list[str],
    tenant: str,
) -> CreateRoleResult:
    return await executor.query_single(
        """\
        INSERT Role {
        	name := <str>$name,
        	scopes := <array<str>>$scopes,
        	tenant := (SELECT Tenant FILTER Tenant.name = <str>$tenant),
        };\
        """,
        name=name,
        scopes=scopes,
        tenant=tenant,
    )


async def create_tenant(
    executor: edgedb.AsyncIOExecutor,
    *,
    tenant: str,
) -> CreateTenantResult:
    return await executor.query_single(
        """\
        INSERT Tenant {
        	name := <str>$tenant
        };\
        """,
        tenant=tenant,
    )


async def create_user(
    executor: edgedb.AsyncIOExecutor,
    *,
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password_hash: str,
    tenant_name: str,
    roles: str,
) -> CreateUserResult:
    return await executor.query_single(
        """\
        INSERT User {
          username := <str>$username,
          email := <str>$email,
          first_name := <str>$first_name,
          last_name := <str>$last_name,
          password_hash := <str>$password_hash,
          tenant := (SELECT Tenant FILTER Tenant.name = <str>$tenant_name),
          roles := (SELECT Role FILTER Role.tenant.name = <str>$tenant_name AND Role.name in <str>$roles)
        };\
        """,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_hash=password_hash,
        tenant_name=tenant_name,
        roles=roles,
    )


async def delete_role(
    executor: edgedb.AsyncIOExecutor,
    *,
    name: str,
    tenant: str,
) -> CreateRoleResult | None:
    return await executor.query_single(
        """\
        DELETE Role
        FILTER
        .name = <str>$name AND .tenant.name = <str>$tenant LIMIT 1;\
        """,
        name=name,
        tenant=tenant,
    )


async def delete_tenant(
    executor: edgedb.AsyncIOExecutor,
    *,
    tenant: str,
) -> CreateTenantResult | None:
    return await executor.query_single(
        """\
        DELETE Tenant FILTER .name = <str>$tenant;\
        """,
        tenant=tenant,
    )


async def delete_user(
    executor: edgedb.AsyncIOExecutor,
    *,
    username: str,
    tenant: str,
) -> CreateUserResult | None:
    return await executor.query_single(
        """\
        DELETE User FILTER .username = <str>$username AND .tenant = (SELECT Tenant FILTER Tenant.name = <str> $tenant);\
        """,
        username=username,
        tenant=tenant,
    )


async def get_user_by_email(
    executor: edgedb.AsyncIOExecutor,
    *,
    email: str,
    tenant: str,
) -> GetUserByEmailResult | None:
    return await executor.query_single(
        """\
        SELECT User {
        	id,
        	username,
        	email,
        	first_name,
        	last_name,
        	password_hash,
        	disabled,
        	roles: { name, scopes},
        	tenant: { name }
        } FILTER .email = <str>$email AND .tenant.name = <str>$tenant LIMIT 1;\
        """,
        email=email,
        tenant=tenant,
    )


async def get_user_by_username(
    executor: edgedb.AsyncIOExecutor,
    *,
    username: str,
    tenant: str,
) -> GetUserByUsernameResult | None:
    return await executor.query_single(
        """\
        SELECT User {
        	id,
        	username,
        	email,
        	first_name,
        	last_name,
        	password_hash,
        	disabled,
        	tenant: {
        	 name
        	},
        	roles: {
        	  name,
        	  scopes
        	}
        } FILTER .username = <str>$username AND .tenant.name = <str>$tenant LIMIT 1;\
        """,
        username=username,
        tenant=tenant,
    )


async def list_roles(
    executor: edgedb.AsyncIOExecutor,
    *,
    tenant: str,
) -> list[ListRolesResult]:
    return await executor.query(
        """\
        SELECT Role {name,scopes,tenant,created_at}
        FILTER
        .tenant.name = <str>$tenant;\
        """,
        tenant=tenant,
    )


async def list_tenants(
    executor: edgedb.AsyncIOExecutor,
) -> list[ListTenantsResult]:
    return await executor.query(
        """\
        SELECT Tenant{name,created_at};\
        """,
    )


async def list_users(
    executor: edgedb.AsyncIOExecutor,
    *,
    tenant: str,
) -> list[ListUsersResult]:
    return await executor.query(
        """\
        SELECT User{username,created_at,tenant:{name}, first_name,last_name,email,password_hash,disabled,roles:{scopes,name}} FILTER .tenant = (SELECT Tenant FILTER Tenant.name = <str> $tenant);\
        """,
        tenant=tenant,
    )


async def read_role(
    executor: edgedb.AsyncIOExecutor,
    *,
    name: str,
    tenant: str,
) -> ListRolesResult | None:
    return await executor.query_single(
        """\
        SELECT Role {name,scopes,tenant,created_at}
        FILTER
        .name = <str>$name AND .tenant.name = <str>$tenant LIMIT 1;\
        """,
        name=name,
        tenant=tenant,
    )


async def read_tenant(
    executor: edgedb.AsyncIOExecutor,
    *,
    tenant: str,
) -> ListTenantsResult | None:
    return await executor.query_single(
        """\
        SELECT Tenant{name,created_at} FILTER .name = <str>$tenant LIMIT 1;\
        """,
        tenant=tenant,
    )


async def read_user(
    executor: edgedb.AsyncIOExecutor,
    *,
    username: str,
    tenant: str,
) -> ListUsersResult | None:
    return await executor.query_single(
        """\
        SELECT User{username,created_at,tenant:{name}, first_name,last_name,email,password_hash,disabled,roles:{scopes,name}} FILTER .username = <str>$username AND .tenant = (SELECT Tenant FILTER Tenant.name = <str> $tenant) LIMIT 1;\
        """,
        username=username,
        tenant=tenant,
    )


async def update_tenant(
    executor: edgedb.AsyncIOExecutor,
    *,
    tenant: str,
    new_tenant: str,
) -> CreateTenantResult | None:
    return await executor.query_single(
        """\
        Update Tenant  
        FILTER .name = <str>$tenant 
        SET { name := <str>$new_tenant};\
        """,
        tenant=tenant,
        new_tenant=new_tenant,
    )
