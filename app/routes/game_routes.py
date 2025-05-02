from flask import request, jsonify, render_template
from app import db, application
from app.models import TypingResult, Paragraph
from flask_login import current_user, login_required
from datetime import datetime, timezone
import json
from sqlalchemy.sql.expression import func # SQLite function that returns a random row

@application.route('/game', methods=['GET'])
def game():
    # Handle game logic here
    return render_template('game/game.html')


@application.route('/random-paragraph', methods=['GET'])
def random_paragraph():
    # pick one row at random
    p = Paragraph.query.order_by(func.random()).first()
    if p is None:
        return jsonify({'error': 'no paragraphs available'}), 404

    return jsonify({
        'paragraph_id': p.paragraph_id,
        'body':         p.body,
        'type':         p.type
    })


@application.route('/submit-instance-statistics', methods=['POST'])
@login_required
def submit_results():
    payload = request.get_json()            

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
        timestamp           = datetime.now(timezone.utc)
    )

    db.session.add(result)
    db.session.commit()

    return jsonify({'status': 'saved', 'result_id': result.result_id})

# test link
@application.route('/results', methods=['GET'])
@login_required
def all_results():
    results = TypingResult.query.filter_by(user_id=current_user.user_id).all()
    return jsonify([
        {
          'result_id': r.result_id,
          'wpm': r.wpm,
          'timestamp': r.timestamp.isoformat()
        } for r in results
    ])