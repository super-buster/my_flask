from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, DataRequired, ValidationError, Email, EqualTo ,Regexp, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('What is your Username?', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username=StringField('Username',validators=[
            DataRequired(),Length(1,64),Regexp(r'^[a-zA-Z]+[a-zA-Z0-9_.]*$',0,
                                               'Usernames must have only letters,'
                                                'numbers ,dots or underscores')])
    password=PasswordField('Password',validators=[
            DataRequired(),EqualTo('password2',message='Password must match.')])
    password2=PasswordField('Confirm password',validators=[DataRequired()])
    submit=SubmitField('Register')

    def validata_email(self,filed):
        if User.query.filter_by(email=filed.data).fist():
            raise ValidationError('Email alread registered!')

    def validata_username(self,filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError('Username alread in use!')