from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login

def create_app(config_class=Config):

    application = Flask(__name__)
    application.config.from_object(Config)
    application.config['SECRET_KEY'] = 'you-will-never-guess'

    db.init_app(application)
    migrate.init_app(application, db)
    login.init_app(application)

    from app import models
    import app.routes.auth_routes
    import app.routes.game_routes
    import app.routes.intro_routes
    import app.routes.main_routes
    import app.routes.stats_routes

    return application
