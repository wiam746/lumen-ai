"""Development entry point. For production use a WSGI server:
    gunicorn "lumen:create_app()"        (Linux/macOS)
    waitress-serve --call lumen:create_app  (Windows)
"""
import os

from lumen import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("LUMEN_DEBUG") == "1" and app.config["LUMEN_ENV"] != "production"
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")), debug=debug)
