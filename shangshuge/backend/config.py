import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'library_secret_key_2024'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_secret_key_2024'
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BORROW_DAYS = 30
    MAX_RENEW_COUNT = 2
    FINE_PER_DAY = 0.5
    MAX_BORROW_COUNT = 5

    CORS_HEADERS = 'Content-Type'