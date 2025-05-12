from flask import Blueprint, request, jsonify, render_template
from app.extensions import db
from app.models import TypingResult, Paragraph
from flask_login import current_user, login_required
from datetime import datetime
import json
from sqlalchemy.sql.expression import func # SQLite function that returns a random row

game_bp = Blueprint('game', __name__)

@game_bp.route('/game', methods=['GET'])
def game():
    # Handle game logic here
    return render_template('game/game.html')


@game_bp.route('/random-paragraph', methods=['GET'])
def random_paragraph():
    p = Paragraph.query.order_by(func.random()).first() # pick a row at random
    if p is None:
        return jsonify({'error': 'no paragraphs available'}), 404

    return jsonify({
        'paragraph_id': p.paragraph_id,
        'body':         p.body,
        'type':         p.type
    }) # return the paragraph as JSON


@game_bp.route('/submit-instance-statistics', methods=['POST'])
@login_required
def submit_results():
    payload = request.get_json() # get the JSON data from the request           

    data = { stat['description']: stat['value'] for stat in payload }

    # Build TypingResult record
    result = TypingResult(
        user_id             = current_user.user_id,
        paragraph_id        = data.get('paragraph id', 1), 
        wpm                 = data.get('words per minute', 0),
        total_characters    = data.get('total characters', 0),
        correct_characters  = json.dumps(data.get('correct characters', {})),
        total_words         = data.get('total words', 0),
        correct_words       = json.dumps(data.get('correct words', {})),
        total_mistakes      = data.get('total mistakes', 0),
        mistake_characters  = json.dumps(data.get('wrong characters', {})),
        timestamp           = datetime.now()
    )

    # If the user is logged in, and they just beat their high-score, then update their highest_wpm.
    if (current_user.is_authenticated):
        if (result.wpm > current_user.highest_wpm):
            current_user.highest_wpm = result.wpm

    db.session.add(result) # add to database
    db.session.commit()

    return jsonify({'status': 'saved', 'result_id': result.result_id}) # return the result ID, client prints it in console
