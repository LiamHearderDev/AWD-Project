from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_login import LoginManager




application = Flask(__name__)
application.config.from_object(Config)
application.config['SECRET_KEY'] = 'you-will-never-guess'
db = SQLAlchemy(application)
migrate = Migrate(application, db)
login = LoginManager(application)
login.login_view = 'login'

from app import models
import app.routes.auth_routes
import app.routes.game_routes
import app.routes.intro_routes
import app.routes.main_routes
import app.routes.stats_routes

if __name__ == '__main__':
    application.run(debug=True)