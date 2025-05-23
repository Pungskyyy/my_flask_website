from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from forms import RegisterForm
from models import User  # pastikan kamu punya model User di models.py

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=25)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6)
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=25)
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6)
    ])
    confirm_password = PasswordField('Konfirmasi Password', validators=[
        DataRequired(), EqualTo('password', message='Password tidak cocok.')
    ])
    submit = SubmitField('Daftar')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username sudah digunakan.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email sudah digunakan.')
