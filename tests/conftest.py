import os
import tempfile

import pytest
from redkitty import create_app
from redkitty.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")

#create and open temporary file for testing
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path, #Override DB Path to use the temporary path & Insert data
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

"""Authentication Testiing"""
class AuthenticationActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email="test1@example.com", password="secret"):
        return self._client.post(
            "/login",
            data={"email": email, "password": password}
        )

    def logout(self):
        return self._client.get("/logout")

@pytest.fixture
def auth(client):
    return AuthenticationActions(client)