import re

import pytest
from cryptography.fernet import Fernet

from lumen import create_app
from lumen.db import connect

PASSWORD = "correct-horse-9"


@pytest.fixture
def app(tmp_path):
    return create_app({
        "LUMEN_ENV": "testing", "SECRET_KEY": "test-secret-key",
        "DATA_ENCRYPTION_KEY": Fernet.generate_key().decode(),
        "DATABASE_PATH": str(tmp_path / "test.db"), "LUMEN_INSTANCE_DIR": str(tmp_path),
        "LLM_PROVIDER": "offline", "ORG_NAME": "Test Org",
        "KNOWLEDGE_BASE_PATH": str(tmp_path / "missing.md"),
    })


@pytest.fixture
def client(app):
    return app.test_client()


def token(client):
    for url in ("/privacy", "/login"):
        match = re.search(r'name="_csrf" value="([^"]+)"', client.get(url).get_data(as_text=True))
        if match:
            return match.group(1)
    raise AssertionError("no CSRF token found")


def post(client, url, data=None, **kw):
    return client.post(url, data={**(data or {}), "_csrf": token(client)}, **kw)


def register(client, username="alice", password=PASSWORD, **extra):
    data = {"username": username, "password": password, "password_confirm": password, "accept_policy": "1", **extra}
    return post(client, "/register", data)


def login(client, username="alice", password=PASSWORD):
    return post(client, "/login", {"username": username, "password": password})


def make_user(app, username, password=PASSWORD, role="user"):
    """Create a user directly in the DB and return a signed-in client."""
    from werkzeug.security import generate_password_hash
    conn = connect(app.config["DATABASE_PATH"])
    conn.execute("INSERT INTO users (username, password_hash, role, policy_version, policy_accepted_at) "
                 "VALUES (?,?,?,?,datetime('now'))", (username, generate_password_hash(password), role, "1.0"))
    conn.commit(); conn.close()
    c = app.test_client()
    assert login(c, username, password).status_code == 302
    return c


def db_query(app, sql, params=()):
    conn = connect(app.config["DATABASE_PATH"])
    rows = conn.execute(sql, params).fetchall()
    conn.commit(); conn.close()
    return rows
