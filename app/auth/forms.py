from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from flask_login import login_user
from .. import db


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():  # self.password.data also OK
            raise ValidationError('Email does not exist.')      # self.field.data not OK

    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if user is not None and user.verify_password(field.data):
            login_user(user, self.remember_me.data)
        else:
            raise ValidationError('Invalid password.')


class RegistrationForm(Form):
    email = StringField('email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('username', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                   'usernames must have only letters, ''numbers, dots or underscores')])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password2',
                                                                             message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
       if User.query.filter_by(email=field.data).first():
           raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')
