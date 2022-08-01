from redkitty import create_app

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_redkitty_welcome(client):
    response = client.get('/redkitty')
    assert response.status_code == 200
    assert b'Welcome to Red Kitty Blog' in response.data
