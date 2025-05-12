import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Base config with defaults for all environments
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    # Use in real deployment. Reads DATABASE_URL from env or falls back to file
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    )

class TestingConfig(Config):
    TESTING = True # Use for running automated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # makes it so that database stored in memory, not on disk
    WTF_CSRF_ENABLED = False # disable CSRF in tests so you can post forms without a token