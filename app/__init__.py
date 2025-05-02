from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_login import LoginManager
from app import models
import app.routes.auth_routes
import app.routes.game_routes
import app.routes.intro_routes
import app.routes.main_routes
import app.routes.stats_routes


application = Flask(__name__)
application.config.from_object(Config)
db = SQLAlchemy(application)
migrate = Migrate(application, db)
login = LoginManager(application)
login.login_view = 'login'


if __name__ == '__main__':
    application.run(debug=True)