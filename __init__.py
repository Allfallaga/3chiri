"""
Package de tests pour l'application 3chiri.

Ce fichier initialise le package de tests et configure les outils nécessaires
pour tester les fonctionnalités de l'application, y compris les routes, les interactions
et les validations des utilisateurs.
"""

import os
import sys

# Ajout du répertoire principal au chemin Python pour permettre l'importation des modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
from app import app, utilisateurs, salles

class BaseTestCase(unittest.TestCase):
    """Classe de base pour les tests unitaires."""

    def setUp(self):
        """
        Configure l'environnement de test avant chaque test.
        """
        # Configure l'application pour le mode test
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Initialiser les données pour les tests
        self.utilisateurs = utilisateurs
        self.salles = salles
        self.utilisateurs.clear()
        self.salles.clear()

    def tearDown(self):
        """
        Nettoie l'environnement de test après chaque test.
        """
        self.app_context.pop()

    def inscrire_utilisateur(self, username, password, confirm, followers=0, social_link=""):
        """
        Inscription d'un utilisateur pour les tests.
        """
        return self.app.post('/inscription', data={
            'username': username,
            'password': password,
            'confirm': confirm,
            'followers': followers,
            'social_link': social_link
        }, follow_redirects=True)

    def connecter_utilisateur(self, username, password):
        """
        Connexion d'un utilisateur pour les tests.
        """
        return self.app.post('/connexion', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def deconnecter_utilisateur(self):
        """
        Déconnexion de l'utilisateur pour les tests.
        """
        return self.app.get('/deconnexion', follow_redirects=True)

# Charger les tests à partir des fichiers de test individuels
# Exemple : from tests.test_routes import TestRoutes
