# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import Required, DataRequired, ValidationError, Email, EqualTo ,Regexp, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('What is your Username?'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    email=StringField(_l('Email'),validators=[DataRequired(),Length(1,64),Email()])
    username=StringField(_l('Username'),validators=[
            DataRequired(),Length(1,64),Regexp(r'^[a-zA-Z]+[a-zA-Z0-9_.]*$',0,
                                               'Usernames must have only letters,'
                                                'numbers ,dots or underscores')])
    password=PasswordField(_l('Password'),validators=[
            DataRequired(),EqualTo('password2',message='Password must match.')])
    password2=PasswordField(_l('Confirm password'),validators=[DataRequired()])
    submit=SubmitField(_l('Register'))

    def validata_email(self,username):
        if User.query.filter_by(email=username.data).first():
            raise ValidationError(_('Email alread registered!'))

    def validata_username(self,email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError(_('Username alread in use!'))


class EditProfileForm(FlaskForm):
    username=StringField(_l('Username'),validators=[
            DataRequired(),Length(1,64),Regexp(r'^[a-zA-Z]+[a-zA-Z0-9_.]*$',0,
                                               'Usernames must have only letters,'
                                                'numbers ,dots or underscores')])
    about_me=TextAreaField(_l('About me'),validators=[Length(0,1024)])
    submit=SubmitField(_l('Submit'))


    def validate_username(self,username):
        if username.data!=self.original_username:
            user=User.query.filter_by(username=self.username.data).first
            if user is not None:
                raise ValidationError(_('Please use a different username'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class RestPasswordForm(FlaskForm):
    password=PasswordField(_l('Password'),validators=[DataRequired()])
    password2=PasswordField(_l('Confirm Password'),validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField(_l('Request Password Reset'))