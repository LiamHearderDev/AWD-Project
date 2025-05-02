from flask import request, jsonify, render_template
from app import db, application
from app.models import TypingResult, Paragraph
from flask_login import current_user, login_required
from datetime import datetime
import json
from sqlalchemy.sql.expression import func # SQLite function that returns a random row

@application.route('/game', methods=['GET'])
def game():
    # Handle game logic here
    return render_template('game/game.html')


@application.route('/random‑paragraph', methods=['GET'])
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
