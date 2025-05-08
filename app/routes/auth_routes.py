import sqlalchemy as sa
from app.models import User
from app.forms import LoginForm, RegistrationForm
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash
from app.extensions import db
from app.models import User
from flask_login import login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('intro'))
    
    # Set the form that we are using. In this case: "LoginForm" from `forms.py`
    form = LoginForm()

    # Check if the form validates. 
    if not form.validate_on_submit():
        # If the form did not validate, render the login page because this was a first time loading.
        return render_template('auth/login.html', form=form)

    # Now we need to get the user from the database.
    try:
        user = db.session.scalar(
            # This does a database query to get the user with the same username.
            sa.select(User).where(User.username == form.username.data))
    # handle any errors from the database query
    except Exception as error:
        flash('An unexpected error occurred while processing your login attempt. Please try again later.')
        return render_template('auth/login.html', form=form)

    # If the user is not found, or if the password is incorrect, reject the login attempt.
    if user is None or not user.check_password(form.password.data):
        flash('Invalid username or password.')
        return render_template('auth/login.html', form=form)
    
    # If the username was found, and the password correct, we log them in.
    login_user(user, remember=form.remember_me.data)
    return redirect(url_for('intro'))

    
    

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    # If the user is already logged in, redirect them to the home page. They can logout there, if they want.
    if current_user.is_authenticated:
        return redirect(url_for('intro'))
    
    # Set the correct form we will be using.
    form = RegistrationForm()

    # If the form does not validate, render the normal page.
    if not form.validate_on_submit():
        print("not validated")
        return render_template('auth/register.html', form=form)
    
    # Create a new user object to go into the database
    user = User(username=form.username.data, email=form.email.data, registration_time=datetime.now())
    user.set_password(form.password.data)

    # Writes the user to the database
    db.session.add(user)
    db.session.commit()

    # Redirects them to login
    flash('Congratulations, you are now a registered user!')
    return redirect(url_for('login'))


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('intro'))