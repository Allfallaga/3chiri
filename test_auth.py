import unittest
from app import app, utilisateurs
from werkzeug.security import generate_password_hash

class TestAuthRoutes(unittest.TestCase):
    """Tests pour les routes d'authentification dans le projet 3chiri."""

    def setUp(self):
        """Configuration avant chaque test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Initialiser les données de test
        utilisateurs.clear()
        utilisateurs['existinguser'] = {
            'username': 'existinguser',
            'password_hash': generate_password_hash('password123'),
            'followers': 20,
            'social_link': 'https://example.com',
            'is_admin': False,
            'role': 'Membre',
            'points': 100,
            'badges': [],
            'transactions': []
        }

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.app_context.pop()

    def test_inscription_success(self):
        """Test d'une inscription réussie."""
        response = self.app.post('/inscription', data={
            'username': 'newuser',
            'password': 'password123',
            'confirm': 'password123',
            'followers': 5,
            'social_link': 'https://example.com'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Inscription réussie", response.data)
        self.assertIn('newuser', utilisateurs)

    def test_inscription_password_mismatch(self):
        """Test d'une inscription avec des mots de passe différents."""
        response = self.app.post('/inscription', data={
            'username': 'newuser',
            'password': 'password123',
            'confirm': 'password456',
            'followers': 5
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Les mots de passe ne correspondent pas", response.data)

    def test_inscription_existing_username(self):
        """Test d'une inscription avec un nom d'utilisateur déjà pris."""
        response = self.app.post('/inscription', data={
            'username': 'existinguser',
            'password': 'password123',
            'confirm': 'password123',
            'followers': 5
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ce nom d'utilisateur est déjà pris", response.data)

    def test_connexion_success(self):
        """Test d'une connexion réussie."""
        response = self.app.post('/connexion', data={
            'username': 'existinguser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Connexion réussie", response.data)

    def test_connexion_invalid_password(self):
        """Test d'une connexion avec un mot de passe incorrect."""
        response = self.app.post('/connexion', data={
            'username': 'existinguser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nom d'utilisateur ou mot de passe incorrect", response.data)

    def test_connexion_nonexistent_user(self):
        """Test d'une connexion avec un utilisateur inexistant."""
        response = self.app.post('/connexion', data={
            'username': 'nonexistentuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nom d'utilisateur ou mot de passe incorrect", response.data)

    def test_deconnexion(self):
        """Test de déconnexion."""
        self.app.post('/connexion', data={
            'username': 'existinguser',
            'password': 'password123'
        }, follow_redirects=True)

        response = self.app.get('/deconnexion', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Vous avez été déconnecté", response.data)

if __name__ == '__main__':
    unittest.main()
