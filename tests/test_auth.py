import pytest
from flask import g, session
from redkitty.db import get_db

"""Registtration Testiing"""

def test_register(client, app):
    assert client.get("/register").status_code == 200
    response = client.post(
        "/register", data={"username": "test", "email": "test@example.com", "password": "secret"})
    assert response.headers["Location"] == "http://localhost/login"

    with app.app_context():
        assert get_db().execute("SELECT * FROM user WHERE username = 'test' ").fetchone() is not None

@pytest.mark.parametrize(("username", "email", "password", "message"), (
    ("", "", "", b"Username is required."),
    ("test", "", "secret", b"Email is required."),
    ("test", "test@example.com", "", b"Password is required."),
    ("test1", "test1@example.com", "secret", b"user is already registered"),
))

def test_register_validate_input(client, username, email, password, message):
    response = client.post(
        "/register",
        data={"username": username, "email": email, "password": password}
    )
    assert message in response.data


"""Login Testing"""

def test_login(client, auth):
    assert client.get("/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "http://localhost/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test1"

@pytest.mark.parametrize(("email", "password", "message"), (
    ("wrong@example.com", "seccret", b"Incorrect Email"),
    ("test1@example.com", "wrongpassword", b"Incorrect Password"),
))

def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data

"""Logout Testing"""
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
