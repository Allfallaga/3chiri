import pytest

def test_inscription_get(client):
    """Test GET request to inscription page"""
    response = client.get('/inscription')
    assert response.status_code == 200

def test_connexion_get(client):
    """Test GET request to login page"""
    response = client.get('/connexion')  
    assert response.status_code == 200

def test_inscription_post(client):
    """Test user registration"""
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'confirm': 'testpass',
        'social_link': 'http://test.com',
        'followers': '100'
    }
    response = client.post('/inscription', data=data)
    assert response.status_code == 302  # Redirect after successful registration
