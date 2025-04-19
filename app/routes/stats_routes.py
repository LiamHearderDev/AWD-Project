from app import application
from flask import render_template

@application.route('/stats', methods=['GET'])
def stats():
    # Handle stats logic here
    return render_template('stats/stats.html')

@application.route('/leaderboard', methods=['GET'])
def leaderboard():
    # Handle stats logic here
    return render_template('stats/leaderboard.html')

@application.route('/shared_stats', methods=['GET'])
def shared_stats():
    # Handle stats logic here
    return render_template('stats/shared_stats.html')