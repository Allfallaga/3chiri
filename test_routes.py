def test_home_route(client):
    """Test de la route GET /."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Bienvenue" in response.data  # Remplacez "Bienvenue" par le contenu attendu de votre page d'accueil

def test_about_route(client):
    """Test de la route GET /about."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b"A propos" in response.data  # Remplacez "A propos" par le contenu attendu de votre page "about"
