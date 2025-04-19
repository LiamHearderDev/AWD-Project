from app import application

@application.route('/game', methods=['GET'])
def game():
    # Handle game logic here
    return "Game Page"


