import pytest

from app import app as flask_app

from flask_login import current_user

@pytest.fixture()
def app():
    flask_app.config.testing = True

    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(autouse=False)
def login(client):
    client.post("/auth/login", data={
        "username": "admin",
        "password": "password"
    })

# ROUTE TESTS

def test_index(client):
    response = client.get("/")
    assert b"Welcome to Ticket Management System" in response.data

def test_login(client):
    response = client.get("/auth/login")

    assert b'<form method="POST">' in response.data
    assert b'"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{5,}"' not in response.data # Should not exist for password in login form

def test_signup(client):
    response = client.get("/auth/signup")

    assert b'<form method="POST">' in response.data
    assert b'"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{5,}"' in response.data # Should exist for password in login form

def test_login_form(client):
    client.post("/auth/login", data={
        "username": "admin",
        "password": "not_correct"
    })

    assert current_user == None or current_user.is_anonymous

    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "password"
    })

    assert response.status_code == 200

def test_signup_and_login(client):
    client.post("/auth/signup", data={
        "username": "test_user",
        "password": "some_password"
    })

    response = client.post("/auth/login", data={
        "username": "test_user",
        "password": "some_password"
    })

    assert response.status_code == 200

@pytest.mark.usefixtures("login")
def test_ticket_create(client):
    response = client.post("/ticket/create", data={
        "title": "Test Title",
        "content": "Testing ticket creation"
    })

    assert response.status_code == 200

def test_ticket_view(client):
    response = client.get("/ticket/12345789")

    assert response.status_code == 302

    response = client.get("/ticket/1")

    assert b"Ticket #1" in response.data
    assert b'Test Title' in response.data

@pytest.mark.usefixtures("login")
def test_ticket_state(client):

    response = client.get("/ticket/1")
    is_open = b"OPEN" in response.data

    response = client.post("/ticket/state", data={
        "ticket_id": 1
    })
    assert response.status_code == 200

    response = client.get("/ticket/1")

    opposite = b"CLOSED" if is_open else b"OPEN"
    assert opposite in response.data

@pytest.mark.usefixtures("login")
def test_ticket_edit(client):
    response = client.get("/ticket/update?ticket_id=1")
    assert b"<legend>Edit ticket 1</legend>" in response.data
    assert b'<input type="text" name="title" class="form-control" value="Test Title">' in response.data

    response = client.post("/ticket/update", data={
        "ticket_id": "1",
        "title": "Test Title",
        "content": "Updated ticket content"
    })
    assert response.status_code == 200

    response = client.get("/ticket/1")
    assert b"Updated ticket content" in response.data

@pytest.mark.usefixtures("login")
def test_ticket_delete(client):
    response = client.post("/ticket/delete", data={
        "ticket_id": "1"
    })
    assert response.status_code == 200

    response = client.get("/ticket/1")
    assert response.status_code == 302

@pytest.mark.usefixtures("login")
def test_logout(client):
    response = client.get("/auth/logout")
    assert response.status_code == 200

    response = client.get("/auth/login")
    assert response.status_code != 302