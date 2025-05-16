from flask import Flask, render_template
from app.config import Config, ProductionConfig
from app.extensions import db, migrate, login, csrf
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

    # This creates a global error handler for all page errors. 
    # Blueprints may override each other, so storing it here will trigger this function regardless of which
    #   blueprint may have caused the error.
    @application.errorhandler(Exception)
    def handle_error_page(e):
        status_code = getattr(e, 'code', 500)   # Get the HTTP error, otherwise use 500.

        # A dictionary of various common HTTP error codes and a message to display to the user.
        status_code_dict = {
            400:  {"title": "Bad Request", "message": "A bad request was received by the server."},
            401:  {"title": "Unauthorized", "message": "You are not authorized to access this page."},
            403:  {"title": "Forbidden", "message": "You do not have permission to access this page."},
            404:  {"title": "Page Not Found", "message": "The page you are looking for could not be found."},
            405:  {"title": "Method Not Allowed", "message": "The method is not allowed for the requested URL."},
            408:  {"title": "Request Timeout", "message": "The request timed out."},
            413:  {"title": "Payload Too Large", "message": "The request is too large for the server to process."},
            429:  {"title": "Too Many Requests", "message": "You have made too many requests."},
            500:  {"title": "Internal Server Error", "message": "An internal server error occurred."},
            502:  {"title": "Bad Gateway", "message": "The server received an invalid response."},
            503:  {"title": "Service Unavailable", "message": "The service is temporarily unavailable."},
            504:  {"title": "Gateway Timeout", "message": "The server took too long to respond."}
        }

        # Get the error title and message. If the code isn't in the dictionary, provide a generic message.
        error_info = status_code_dict.get(status_code, {"title": "Error", "message": "An unexpected error occurred."})
        
        return render_template(
            'errors/generic_error.html',
            code=status_code,
            title=error_info["title"],
            message=error_info["message"]
        ), status_code

    return application
