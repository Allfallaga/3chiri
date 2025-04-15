import pytest
from main import create_app  # Assurez-vous que votre application Flask est créée via une factory.

@pytest.fixture
def app():
    """
    Fixture pour fournir l'application Flask en mode test.
    """
    app = create_app()  # Crée une instance de l'application Flask via la factory
    app.config.update({
        "TESTING": True,  # Active le mode test
        "SECRET_KEY": "test_secret_key",  # Clé secrète pour les tests
    })
    return app

@pytest.fixture
def client(app):
    """
    Fixture pour fournir un client de test.
    """
    return app.test_client()  # Retourne un client de test pour simuler des requêtes HTTP

@pytest.fixture
def runner(app):
    """
    Fixture pour fournir un runner CLI.
    """
    return app.test_cli_runner()  # Retourne un runner pour tester les commandes CLI
