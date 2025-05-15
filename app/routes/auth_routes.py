import sqlalchemy as sa
from app.models import User
from app.forms import LoginForm, RegistrationForm
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from flask_login import login_user, logout_user, current_user, login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('intro.intro'))
    
    # Set the form that we are using. In this case: "LoginForm" from `forms.py`
    form = LoginForm()

    # Check if the form validates. 
    if not form.validate_on_submit():
        # If the form did not validate, render the login page because this was a first time loading.
        return render_template('auth/login.html', form=form)

    try:
        # This does a database query to get the user with the same username.
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data)) 
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
    return redirect(url_for('intro.intro'))

    
    

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    # If the user is already logged in, redirect them to the home page. They can logout there, if they want.
    if current_user.is_authenticated:
        return redirect(url_for('intro.intro'))
    
    # Set the correct form we will be using.
    form = RegistrationForm()

    # If the form does not validate, render the normal page.
    if not form.validate_on_submit():
        # print("not validated") 
        return render_template('auth/register.html', form=form)
    
    # Create a new user object to go into the database
    user = User(username=form.username.data, email=form.email.data, registration_time=datetime.now())
    user.set_password(form.password.data)

    # Writes the user to the database
    db.session.add(user)
    db.session.commit()

    # Redirects them to login
    flash('Congratulations, you are now a registered user!')

    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('intro.intro'))


@auth_bp.route('/get_current_user', methods=['GET'])
def get_current_user() -> User | None:
    """
    This route is used to get the current user's information. It returns a JSON object with the user's ID, username, email, registration time, and highest WPM.
    This is primarily used by unit tests to check if the user is logged in and has the correct information. This can ONLY be used during tests, as it is not a route that is used in the application.
    """
    if current_user.is_authenticated:
        return {
            'user_id': current_user.user_id,
            'username': current_user.username,
            'email': current_user.email,
            'registration_time': current_user.registration_time,
            'highest_wpm': current_user.highest_wpm
        }
    else:
        return {"error": "User is not logged in."}