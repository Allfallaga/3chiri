import unittest
from app import app, utilisateurs, salles

class TestDashboardRoutes(unittest.TestCase):
    """Tests pour les routes du tableau de bord."""

    def setUp(self):
        """Configuration avant chaque test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Initialiser les données pour les tests
        utilisateurs.clear()
        salles.clear()
        utilisateurs['testuser'] = {
            'username': 'testuser',
            'password_hash': 'fakehash',
            'followers': 10,
            'social_link': '',
            'is_admin': False,
            'role': 'Membre',
            'points': 100,
            'badges': [],
            'transactions': []
        }

    def tearDown(self):
        """Nettoyage après chaque test."""
        self.app_context.pop()

    def test_dashboard_access_without_login(self):
        """Test l'accès au tableau de bord sans connexion."""
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Veuillez vous connecter pour accéder à votre tableau de bord", response.data)

    def test_dashboard_access_with_login(self):
        """Test l'accès au tableau de bord avec une connexion valide."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Tableau de bord", response.data)

    def test_wallet_recharge_valid(self):
        """Test d'une recharge valide du portefeuille."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        response = self.app.post('/wallet/recharger', data={
            'montant': 50
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Votre portefeuille a été rechargé de 50 points", response.data)
        self.assertEqual(utilisateurs['testuser']['points'], 150)

    def test_wallet_recharge_invalid_amount(self):
        """Test d'une recharge avec un montant invalide."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        response = self.app.post('/wallet/recharger', data={
            'montant': -10
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Montant invalide pour la recharge", response.data)

    def test_wallet_recharge_not_logged_in(self):
        """Test d'une tentative de recharge sans être connecté."""
        response = self.app.post('/wallet/recharger', data={
            'montant': 50
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Veuillez vous connecter pour recharger votre portefeuille", response.data)

if __name__ == '__main__':
    unittest.main()
