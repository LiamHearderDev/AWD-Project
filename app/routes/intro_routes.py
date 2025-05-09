from app.extensions import db
from flask import render_template, Blueprint

intro_bp = Blueprint('intro', __name__)

@intro_bp.route('/')
@intro_bp.route('/intro')
def intro():
    return render_template('intro/intro.html')

@intro_bp.route('/about')
def about():
    return "About"
