from dotenv import load_dotenv
from edgedb import create_async_client
from fastapi import FastAPI
from uvicorn import run

from libauthproxy.routes import register_routes

if __name__ == '__main__':
    load_dotenv()
    app = FastAPI()
    conn = create_async_client()
    register_routes(app, conn)
    run(app, host="0.0.0.0", port=1337)
