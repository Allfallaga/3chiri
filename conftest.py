import pytest
from main import app

@pytest.fixture
def app():
    return app

@pytest.fixture
def client(app):
    return app.test_client()
