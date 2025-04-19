from flask import Flask

application = Flask(__name__)

import app.routes.auth_routes
import app.routes.game_routes
import app.routes.intro_routes
import app.routes.main_routes
import app.routes.stats_routes

if __name__ == '__main__':
    application.run(debug=True)


# def create_app():

#     # import and register each module’s routes
#     from app.routes.auth_routes  import init_auth_routes
#     from app.routes.intro_routes  import init_intro_routes
#     from app.routes.main_routes  import init_main_routes
#     from app.routes.game_routes  import init_game_routes
#     from app.routes.stats_routes import init_stats_routes

#     # Deprecated functions. 
#     init_auth_routes(app)
#     init_main_routes(app)
#     init_game_routes(app)
#     init_intro_routes(app)
#     init_stats_routes(app)

#     return app