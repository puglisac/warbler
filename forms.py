from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email



class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class EditUserForm(FlaskForm):
    """update user form"""
    username = StringField('Username')
    email = StringField('E-mail', validators=[Email()])
    image_url = StringField('Image URL')
    header_image_url = StringField('Image URL')
    bio = StringField('Bio')
    password = PasswordField('Password')
    is_admin = BooleanField('Admin')


class NewPasswordForm(FlaskForm):
    """form to change password"""
    cur_password = PasswordField(
        'Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    conf_password = PasswordField(
        'Confirm New Password', validators=[DataRequired()])
