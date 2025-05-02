from app import application, db
from flask import render_template, redirect, flash, url_for
from flask_login import current_user, login_user
import sqlalchemy as sa
from app.models import User
from app.forms import LoginForm


@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('intro'))
    
    # Set the form that we are using. In this case: "LoginForm" from `forms.py`
    form = LoginForm()

    # Check if the form validates. 
    if form.validate_on_submit():
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

    # If the form did not validate, render the login page because this was a first time loading.
    return render_template('auth/login.html', form=form)
    

@application.route('/register', methods=['GET', 'POST'])
def register():
    # Handle registration logic here
    return render_template('auth/register.html')

