from uvicorn import run
from authproxy import init_app

if __name__ == '__main__':
    app = init_app()
    run(app, host="0.0.0.0", port=1337)
