from app import application
from flask import render_template

@application.route('/game', methods=['GET'])
def game():
    # Handle game logic here
    return render_template('game/game.html')
