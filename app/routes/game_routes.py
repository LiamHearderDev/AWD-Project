
def init_game_routes(app):

    @app.route('/game', methods=['GET'])
    def game():
        # Handle game logic here
        return "Game Page"


