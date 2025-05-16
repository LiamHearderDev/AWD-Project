from flask import Blueprint, request, jsonify, render_template
from app.extensions import db
from app.models import TypingResult, Paragraph
from flask_login import current_user, login_required
from datetime import datetime
import json
from sqlalchemy.sql.expression import select, func # SQLite function that returns a random row
from sqlalchemy.exc import SQLAlchemyError


game_bp = Blueprint('game', __name__)

@game_bp.route('/game', methods=['GET'])
def game():
    # Handle game logic here
    return render_template('game/game.html')


@game_bp.errorhandler(SQLAlchemyError) # runs if adding to database causes error
def handle_db_error(e):
    db.session.rollback()
    return jsonify(error="Database error, please try again"), 500


@game_bp.route('/random-paragraph', methods=['GET'])
def random_paragraph():
    p = db.session.scalars(select(Paragraph).order_by(func.random())).first() # pick a row at random
    if p is None:
        return jsonify({'error': 'no paragraphs available'}), 404

    return jsonify({
        'paragraph_id': p.paragraph_id,
        'body':         p.body,
        'type':         p.type
    }) # return the paragraph as JSON

ALLOWED_STATS = { # whitelist dictionary with correct datatypes of each column
    'paragraph id':         int,
    'words per minute':     int,
    'total characters':     int,
    'correct characters':   dict,
    'total words':          int,
    'correct words':        dict,
    'total mistakes':       int,
    'wrong characters':     dict,
    'wrong words':          dict
}

@game_bp.route('/submit-instance-statistics', methods=['POST'])
@login_required
def submit_results():
    payload = request.get_json(silent=True) # get the JSON data from the request, even if invalid          
    if not isinstance(payload, list): # check if is actually JSON
        return jsonify(error="Expected a JSON array of stats"), 400

    data = {}
    for i, stat in enumerate(payload):
        # must be an object with exactly description+value
        if not isinstance(stat, dict) or 'description' not in stat or 'value' not in stat:
            return jsonify(error=f"Item {i} must be an object with 'description' and 'value'"), 400

        desc = stat['description']
        val  = stat['value']

        # description must be in our whitelist
        if desc not in ALLOWED_STATS:
            return jsonify(error=f"Unexpected stat description: '{desc}'"), 400

        # value must be the right type
        expected_type = ALLOWED_STATS[desc]
        if not isinstance(val, expected_type):
            return jsonify(error=f"Value for '{desc}' must be a {expected_type.__name__}"), 400

        # is numeric, must be valid in context
        if expected_type is int and val < 0:
            return jsonify(error=f"Value for '{desc}' must be non-negative"), 400

        data[desc] = val # add valid statistic to data dictionary
    
    # validate paragraph exists (unless it’s -1 for placeholder)
    pid = data.get('paragraph id', -1)
    if pid != -1 and db.session.get(Paragraph, pid) is None:
        return jsonify(error=f"No paragraph found with id {pid}"), 400

    # Build TypingResult record with validated data
    result = TypingResult(
        user_id             = current_user.user_id,
        paragraph_id        = pid,
        wpm                 = data['words per minute'],
        total_characters    = data['total characters'],
        total_words         = data['total words'],
        correct_characters  = json.dumps(data['correct characters']),
        correct_words       = json.dumps(data['correct words']),
        total_mistakes      = data['total mistakes'],
        mistake_characters  = json.dumps(data['wrong characters']),
        mistake_words       = json.dumps(data['wrong words']),
        timestamp           = datetime.now()
    )

    # If the user is logged in, and they just beat their high-score, then update their highest_wpm.
    if (current_user.is_authenticated):
        if (result.wpm > current_user.highest_wpm):
            current_user.highest_wpm = result.wpm

    db.session.add(result)
    db.session.commit()

    return jsonify({'status': 'saved', 'result_id': result.result_id}), 200 # return the result ID, client prints it in console
