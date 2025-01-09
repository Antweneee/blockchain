import pytest
from flask import Flask
from backend.main import create_app  # Assuming create_app is used to initialize the Flask app
from backend.models import db, User, Asset

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Register a test user
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201

    # Login to get a session
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200

    return {'Authorization': f"Bearer {response.get_json()['user']['id']}"}

def test_register_user(client):
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['user']['email'] == 'new@example.com'

def test_login_user(client):
    # Register first
    client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testlogin@example.com',
        'password': 'password123'
    })

    # Login
    response = client.post('/auth/login', json={
        'email': 'testlogin@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'user' in data
    assert data['user']['email'] == 'testlogin@example.com'

def test_create_asset(client, auth_headers):
    response = client.post('/assets', json={
        'title': 'Test Asset',
        'description': 'This is a test asset.',
        'metadata_url': 'http://example.com/metadata.json',
        'transfer_fee': 10
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data['asset']['title'] == 'Test Asset'

def test_get_assets(client):
    response = client.get('/assets')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_asset_by_id(client):
    # Create a dummy asset
    client.post('/assets', json={
        'title': 'Test Asset',
        'description': 'This is a test asset.',
        'metadata_url': 'http://example.com/metadata.json',
        'transfer_fee': 10
    })

    # Get the asset
    response = client.get('/assets/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Asset'