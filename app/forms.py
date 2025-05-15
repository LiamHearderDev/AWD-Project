


###### Imports ######

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User



###### Validation Functions ######

def validate_datatype(datatype: type, strict: bool = False):
    """Validator to check if the data is of the expected type. Raises a ValidationError if not. 
    The 'Strict' parameter determines if we check the field's raw_data attribute instead of the field's data attribute.
    This is useful for fields that require strict type validation, such as the username and password fields."""

    def _validate(form, field): # This is a factory function that returns a validator function.
        # We first decide how strict we want to be. This should not be used for all fields, as some require more flexibility; for example, the "remember me" checkbox.
        # If strict is True, we check the raw_data first. This is to ensure STRICT type validation.
        if strict:
            if field.raw_data: 
                if not isinstance(field.raw_data[0], datatype):
                    raise ValidationError(f'Invalid data type. Expected {datatype.__name__}, got {type(field.raw_data[0]).__name__}.')
        # Fallback to checking field.data
        elif not isinstance(field.data, datatype):
            raise ValidationError(f'Invalid data type. Expected {datatype.__name__}, got {type(field.data).__name__}.')
    return _validate



###### Form Classes ######

class LoginForm(FlaskForm):
    """Form for user login. Contains fields for username, password, and a remember me checkbox.
    The form uses Flask-WTF for CSRF protection and WTForms for validation. """

    # Fields
    username    = StringField('Username',                   validators=[DataRequired(), validate_datatype(str, True)])
    password    = PasswordField('Password',                 validators=[DataRequired(), validate_datatype(str, True)])
    remember_me = BooleanField('Remember Me', default=False,validators=[validate_datatype(bool)])
    submit      = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Form for user registration. Contains fields for username, email, password, and password confirmation."""

    # Fields
    username    = StringField('Username',           validators=[DataRequired(), validate_datatype(str, True)])
    email       = StringField('Email',              validators=[DataRequired(), validate_datatype(str), Email()])
    password    = PasswordField('Password',         validators=[DataRequired(), validate_datatype(str, True)])
    password2   = PasswordField('Repeat Password',  validators=[DataRequired(), EqualTo('password'), validate_datatype(str, True)])
    submit      = SubmitField('Register')

    # Validation
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('This username has been taken. Please try another.')
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('An account is already registered to this email.')


class FriendRequestForm(FlaskForm): # Using user id
    """Form for sending a friend request. Contains a field for the user_id of the user to send the request to."""

    # Fields
    user_id     = IntegerField('User ID', validators=[DataRequired(), validate_datatype(int, True)])
    submit      = SubmitField('Send Request')

class FriendRequestByUsernameForm(FlaskForm): # Using user name 
    username = StringField('Username', validators=[DataRequired()])
    submit   = SubmitField('Send Request')
