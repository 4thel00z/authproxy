from dotenv import load_dotenv
from edgedb import create_async_client
from fastapi import FastAPI

from libauthproxy.routes import register_routes


def init_app(*args, **kwargs) -> FastAPI:
    load_dotenv()
    app = kwargs.get("app", FastAPI())
    conn = kwargs.get("db", create_async_client())
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("app", None) # None so this does not raise
    kwargs_copy.pop("db", None)
    register_routes(app, conn, **kwargs_copy)
    return app
