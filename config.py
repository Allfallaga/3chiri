import os

class Config:
    """Configuration de base pour l'application Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre_cle_secrete'
    DEBUG = False
    TESTING = False

    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///3chiri.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration des emails
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # D'autres configurations spécifiques
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limite de 16 Mo pour les téléchargements de fichiers
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration pour l'environnement de test."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_3chiri.db'


class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    DEBUG = False
    TESTING = False


# Choisir la configuration appropriée en fonction de l'environnement
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
