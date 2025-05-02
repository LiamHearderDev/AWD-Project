from app import application, db
from flask import render_template
from flask_login import current_user, login_user
import sqlalchemy as sa
from app.models import User
from app.forms import LoginForm

@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('intro/intro.html')
    form = LoginForm()
    return render_template('auth/login.html', form=form)

@application.route('/register', methods=['GET', 'POST'])
def register():
    # Handle registration logic here
    return render_template('auth/register.html')

