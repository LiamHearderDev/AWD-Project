from app import application
from flask import render_template

@application.route('/')
@application.route('/intro')
def intro():
    return render_template('intro/intro.html')

@application.route('/about')
def about():
    return "About"
