# Database imports
from app import db
from sqlalchemy.types import JSON

# Login imports
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# This is a class defining each user account that has been registered.
class User(UserMixin, db.Model):

    # The fields of the user table in the database
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    registration_time = db.Column(db.DateTime, nullable=False)
    highest_wpm = db.Column(db.Integer, default=0) # TODO: This is only used for the leaderboards. May not need this as we can extract from TypingResult table... 

    # Defines how this class is printed
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    # Encrypts an un-hashed password and sets it as the hashed password
    def set_password(self, password_plain_text):
        self.password = generate_password_hash(password_plain_text)
    
    # Checks if the plain text, when hashed, is the same as the stored password.
    def check_password(self, password_plain_text):
        return check_password_hash(self.password, password_plain_text)
    
    def get_id(self):
        return str(self.user_id)


# This is a class defining the result of an individual game.
# Each one of these will be assigned to a user, which we can then extract and analyze to get a user's statistics.
class TypingResult(db.Model):
    __tablename__ = 'result'
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraph.paragraph_id'), nullable=False)
    wpm = db.Column(db.Integer, default=0)
    total_characters = db.Column(db.Integer,nullable=False)
    correct_characters = db.Column(JSON, nullable=False)
    total_words = db.Column(db.Integer, nullable=False)
    correct_words = db.Column(JSON, nullable=False)
    total_mistakes = db.Column(db.Integer, nullable=False)
    mistake_characters = db.Column(JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return '<TypingResult(WPM) {}>'.format(self.wpm)


# This is a class defining the text displayed in a game. We will store many of these.
class Paragraph(db.Model):
    __tablename__ = 'paragraph'
    paragraph_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.String(300), nullable=False)
    type = db.Column(db.String(32), nullable=True) # "normal", "gibberish", "coding"

    def __repr__(self):
        return '<Paragraph {}>'.format(self.body)


# This is a class defining the friendship between users.
# The PK is a composite key of user_id and friend_id. There will only be one friendship between two users, so these must be unique.
# This is a strange table and it may be subsequent to change. BE WARNED.
class Friendship(db.Model):
    __tablename__ = 'friendship'
    # user_id and friend_id is composite primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, nullable=False)
    friend_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),primary_key=True, nullable=False)
    is_requested = db.Column(db.Boolean, nullable=False)
    requesting_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"<Friendship: {self.user_id}> and {self.friend_id}, requested={self.is_requested}"
    

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))