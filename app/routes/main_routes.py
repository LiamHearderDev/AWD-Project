from app import application
from flask import render_template

@application.route('/dashboard', methods=['GET'])
def dashboard():
    # Handle main logic here
    return render_template('main/dashboard.html')

@application.route('/profile', methods=['GET'])
def profile():
    return render_template('main/profile.html')

# TODO: Add a page in for this:
# @application.errorhandler(404)
# def page_not_found(e):
#     return render_template('errors/404.html'), 404