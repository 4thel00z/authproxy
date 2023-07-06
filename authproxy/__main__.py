from uvicorn import run
from authproxy import init_app
from libauthproxy import HOST, PORT

if __name__ == '__main__':
    app = init_app()
    run(app, host=HOST, port=PORT)
