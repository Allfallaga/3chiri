import unittest
from app import app, utilisateurs, salles

class TestRoomsRoutes(unittest.TestCase):
    """Tests pour les routes de gestion des salons."""

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

    def test_access_rooms_without_login(self):
        """Test de l'accès à la gestion des salons sans connexion."""
        response = self.app.get('/rooms', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Veuillez vous connecter pour accéder aux salons", response.data)

    def test_create_room_success(self):
        """Test de création d'un salon avec succès."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        response = self.app.post('/rooms', data={
            'nom': 'Test Room',
            'type': 'public',
            'code': '',
            'cost': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Le salon 'Test Room' a été créé avec succès", response.data)
        self.assertEqual(len(salles), 1)

    def test_create_room_without_name(self):
        """Test de création d'un salon sans nom."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        response = self.app.post('/rooms', data={
            'nom': '',
            'type': 'public',
            'code': '',
            'cost': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Le nom de la salle est requis", response.data)

    def test_join_private_room_with_correct_code(self):
        """Test de rejoindre un salon privé avec le bon code."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        # Créer un salon privé
        salles[1] = {
            'id': 1,
            'nom': 'Private Room',
            'type': 'prive',
            'owner': 'testuser',
            'code': '1234',
            'cost': None,
            'participants': {},
            'messages': [],
            'banned': set()
        }

        response = self.app.post('/room/1', data={
            'action': 'enter',
            'code': '1234'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Vous avez rejoint le salon", response.data)

    def test_join_private_room_with_wrong_code(self):
        """Test de rejoindre un salon privé avec un code incorrect."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        # Créer un salon privé
        salles[1] = {
            'id': 1,
            'nom': 'Private Room',
            'type': 'prive',
            'owner': 'testuser',
            'code': '1234',
            'cost': None,
            'participants': {},
            'messages': [],
            'banned': set()
        }

        response = self.app.post('/room/1', data={
            'action': 'enter',
            'code': 'wrongcode'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Code d'accès incorrect", response.data)

    def test_create_paid_room_with_valid_cost(self):
        """Test de création d'un salon payant avec un coût valide."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        response = self.app.post('/rooms', data={
            'nom': 'Paid Room',
            'type': 'payant',
            'code': '',
            'cost': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Le salon 'Paid Room' a été créé avec succès", response.data)
        self.assertEqual(salles[1]['cost'], 20)

    def test_create_paid_room_with_invalid_cost(self):
        """Test de création d'un salon payant avec un coût invalide."""
        with self.app.session_transaction() as session:
            session['username'] = 'testuser'

        response = self.app.post('/rooms', data={
            'nom': 'Invalid Paid Room',
            'type': 'payant',
            'code': '',
            'cost': '-10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Le coût doit être un nombre entier valide", response.data)

if __name__ == '__main__':
    unittest.main()
