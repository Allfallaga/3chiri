import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

# Génère un mot de passe hashé
def hash_password(password):
    """
    Hash a plain text password using Werkzeug.
    Args:
        password (str): The plain text password.
    Returns:
        str: The hashed password.
    """
    return generate_password_hash(password)

# Vérifie un mot de passe avec son hash
def verify_password(hashed_password, password):
    """
    Verify a password against its hash.
    Args:
        hashed_password (str): The hashed password.
        password (str): The plain text password.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return check_password_hash(hashed_password, password)

# Génère un code aléatoire pour les salons privés
def generate_room_code(length=6):
    """
    Generate a random alphanumeric code for private rooms.
    Args:
        length (int): The length of the code. Default is 6.
    Returns:
        str: The generated code.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Formate une chaîne de texte pour le rendre plus lisible
def format_text(text):
    """
    Capitalize the first letter of each word in a string.
    Args:
        text (str): The input text.
    Returns:
        str: The formatted text.
    """
    return ' '.join(word.capitalize() for word in text.split())

# Vérifie si une chaîne est un email valide
def is_valid_email(email):
    """
    Check if the given string is a valid email address.
    Args:
        email (str): The email address to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Convertit une liste en dictionnaire avec des index
def list_to_dict(lst):
    """
    Convert a list to a dictionary with indices as keys.
    Args:
        lst (list): The input list.
    Returns:
        dict: A dictionary with indices as keys and list items as values.
    """
    return {index: value for index, value in enumerate(lst)}
