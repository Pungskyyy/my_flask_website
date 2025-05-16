import os

class Config:
    SECRET_KEY = os.urandom(24)  # Kunci untuk CSRF dan session
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Database SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
