from app import db
from sqlalchemy.types import JSON

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    registration_time = db.Column(db.DateTime, nullable=False)
    highest_wpm = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class TypingResult(db.Model):
    __tablename__ = 'result'
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraph.paragraph_id'), nullable=False)
    wpm = db.Column(db.Integer, default=0)
    total_characters = db.Column(db.Integer,nullable=False)
    characters = db.Column(JSON, nullable=False)
    total_words = db.Column(db.Integer, nullable=False)
    words = db.Column(JSON, nullable=False)
    correct_words = db.Column(JSON, nullable=False)
    total_mistakes = db.Column(db.Integer, nullable=False)
    mistake_characters = db.Column(JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return '<TypingResult(WPM) {}>'.format(self.wpm)

class Paragraph(db.Model):
    __tablename__ = 'paragraph'
    paragraph_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.String(300), nullable=False)
    type = db.Column(db.String(32), nullable=True)

    def __repr__(self):
        return '<Paragraph {}>'.format(self.body)

class Friendship(db.Model):
    __tablename__ = 'friendship'
    # user_id and friend_id is composite primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, nullable=False)
    friend_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),primary_key=True, nullable=False)
    is_requested = db.Column(db.Boolean, nullable=False)
    requesting_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"<Friendship: {self.user_id}> and {self.friend_id}, requested={self.is_requested}"