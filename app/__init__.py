from flask import Flask, render_template
from app.config import Config, ProductionConfig
from app.extensions import db, migrate, login, csrf, mail
from dotenv import load_dotenv
def create_app(config_class=ProductionConfig):

    # Loads configuration variables from the environment
    load_dotenv()

    application = Flask(__name__)
    application.config.from_object(config_class)

    db.init_app(application)
    migrate.init_app(application, db)
    login.init_app(application)
    csrf.init_app(application)

    mail.init_app(application)

    # Imports every route from their respective files
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
    application.register_blueprint(friends_bp)

    # This creates a global error handler for all 404 errors. 
    # Blueprints may override each other, so storing it here will trigger this function regardless of which
    #   blueprint may have caused the error.
    @application.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    return application
