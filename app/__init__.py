from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login

def create_app(config_class=Config):

    application = Flask(__name__)
    application.config.from_object(config_class)
    application.config['SECRET_KEY'] = 'you-will-never-guess'

    db.init_app(application)
    migrate.init_app(application, db)
    login.init_app(application)

    from app.routes.auth_routes import auth_bp
    from app.routes.game_routes import game_bp
    from app.routes.intro_routes import intro_bp
    from app.routes.main_routes import main_bp
    from app.routes.stats_routes import stats_bp
    from app.routes.friend_routes import friends_bp 

    application.register_blueprint(auth_bp)
    application.register_blueprint(game_bp)
    application.register_blueprint(intro_bp)
    application.register_blueprint(main_bp)
    application.register_blueprint(stats_bp)

    return application
