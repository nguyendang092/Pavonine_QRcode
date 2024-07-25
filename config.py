import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('your_database_uri', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
