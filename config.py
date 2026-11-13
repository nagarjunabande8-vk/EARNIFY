import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'earnify-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///earnify.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
