import pytest
from main import app  # Importez votre application Flask depuis main.py

@pytest.fixture
def app():
    """Fixture pour fournir l'application Flask."""
    app.config.update({
        "TESTING": True,  # Active le mode test
        "SECRET_KEY": "test_secret_key",  # Clé secrète pour les tests
    })
    return app

@pytest.fixture
def client(app):
    """Fixture pour fournir un client de test."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture pour fournir un runner CLI."""
    return app.test_cli_runner()
