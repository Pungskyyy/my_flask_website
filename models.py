from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Kolom tambahan untuk tracking login
    is_online = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

    def check_password(self, password):
        # Contoh pengecekan password (sesuaikan dengan cara hashing kamu)
        return self.password == password
