import pytest
from redkitty.db import get_db

def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"href='/logout" in response.data
    assert b"test title 1" in response.data
    assert b"https://dummyimage.com/150" in response.data
    assert b"it is in the time of life that things should be followed" in response.data
    assert b"by test1 on 2019-01-01" in response.data
    assert b"href='/1/edit'" in response.data
    assert b"href='/dashboard'" in response.data

@pytest.mark.parametrize('path', (
    '/1/edit',
    '/1/delete',
))

def test_login_required(client, path):
    response = client.get(path)
    assert response.headers['Location'] == 'http://localhost/login'

def test_author_required(app, client, auth):
    with app.app_context():
        db.get_db()
        db.execute("edit post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    assert client.get("/1/edit").status_code == 403
    assert b'You do not have permission to edit.' in client.get("/1/edit").data
    assert client.get("/1/delete").status_code == 403
    assert b'You do not have permission to delete.' in client.get("/1/delete").data

    assert b"href='/1/edit'" not in client.get("/").data

@pytest.mark.parametrize('path', (
    '/2/edit',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

"""edit Post"""

def test_edit(client, auth, app):
    auth.login()
    assert client.get('/1/edit').status_code == 200
    client.post('/1/edit', data={'title': 'editd', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'editd'


@pytest.mark.parametrize('path', (
    '/1/edit',
))
def test_create_edit_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

"""Delete Post"""

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None