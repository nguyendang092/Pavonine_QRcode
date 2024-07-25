import pytest
from app import create_app, db
from app.models import Record

@pytest.fixture
def app():
    app = create_app('app.config.Config')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the Home Page' in response.data
