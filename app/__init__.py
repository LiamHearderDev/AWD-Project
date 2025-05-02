from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import Config


application = Flask(__name__)

application.config.from_object(Config)

db = SQLAlchemy(application)
migrate = Migrate(application, db)


from app import models

import app.routes.auth_routes
import app.routes.game_routes
import app.routes.intro_routes
import app.routes.main_routes
import app.routes.stats_routes

if __name__ == '__main__':
    application.run(debug=True)

