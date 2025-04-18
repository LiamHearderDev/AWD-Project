from flask import Flask

def create_app():
    app = Flask(__name__)
    # … any config / extensions …

    # import and register each module’s routes
    from .routes.auth_routes  import init_auth_routes
    from .routes.intro_routes  import init_intro_routes
    from .routes.main_routes  import init_main_routes
    from .routes.game_routes  import init_game_routes
    from .routes.stats_routes import init_stats_routes

    init_auth_routes(app)
    init_main_routes(app)
    init_game_routes(app)
    init_intro_routes(app)
    init_stats_routes(app)

    return app
