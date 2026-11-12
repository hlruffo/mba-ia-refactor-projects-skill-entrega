"""Flask entry point; application setup lives in the loja package factory."""

from config import Config
from loja import create_app

settings = Config()
app = create_app(settings)


if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
