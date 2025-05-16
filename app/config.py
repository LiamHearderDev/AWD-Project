import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Base config with defaults for all environments
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail settings:
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

class ProductionConfig(Config):
    # Use in real deployment. Reads DATABASE_URL from env or falls back to file
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    )
    WTF_CSRF_ENABLED = True

class TestingConfig(Config):
    TESTING = True # Use for running automated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # makes it so that database stored in memory, not on disk
    WTF_CSRF_ENABLED = False # disable CSRF in tests so you can post forms without a token
    SECRET_KEY = 'test-secret-key'

    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = 'sender@gmail.com'

