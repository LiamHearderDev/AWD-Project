from app import db
from flask import render_template, Blueprint
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # Handle main logic here
    return render_template('main/dashboard.html')

@main_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('main/profile.html')