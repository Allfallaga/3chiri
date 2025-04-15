from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rooms = db.relationship('Room', secondary='user_room', back_populates='users')

    def __repr__(self):
        return f'<User {self.username}>'

# Modèle pour les salons
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # public, privé, payant
    cost = db.Column(db.Integer, nullable=True)  # Optionnel pour les salons payants
    code = db.Column(db.String(10), nullable=True)  # Optionnel pour les salons privés
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', secondary='user_room', back_populates='rooms')

    def __repr__(self):
        return f'<Room {self.nom}>'

# Table d'association pour les utilisateurs et les salons
user_room = db.Table('user_room',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)
