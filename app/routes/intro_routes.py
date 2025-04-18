
def init_intro_routes(app):
    @app.route('/')
    @app.route('/index')
    def index():
        return "Intro Page"



