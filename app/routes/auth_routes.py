from app import application
from flask import render_template

@application.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login logic here
    return render_template('auth/login.html')

@application.route('/register', methods=['GET', 'POST'])
def register():
    # Handle registration logic here
    return render_template('auth/register.html')

