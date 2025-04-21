from app import application
from flask import render_template

@application.route('/dashboard', methods=['GET'])
def dashboard():
    # Handle main logic here
    return render_template('main/dashboard.html')

@application.route('/profile', methods=['GET'])
def profile():
    return render_template('main/profile.html')