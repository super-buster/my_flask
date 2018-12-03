from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
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

    def validata_email(self,username):
        if User.query.filter_by(email=username.data).first():
            raise ValidationError('Email alread registered!')

    def validata_username(self,email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Username alread in use!')


class EditProfileForm(FlaskForm):
    username=StringField('Username',validators=[
            DataRequired(),Length(1,64),Regexp(r'^[a-zA-Z]+[a-zA-Z0-9_.]*$',0,
                                               'Usernames must have only letters,'
                                                'numbers ,dots or underscores')])
    about_me=TextAreaField('About me',validators=[Length(0,1024)])
    submit=SubmitField('Submit')

    #继承Flask的__init__方法
    def __init__(self,original_username,*args,**kwargs):
        super(EditProfileForm, self).__init__(*args,**kwargs)
        self.original_username=original_username

    def validate_username(self,username):
        if username.data!=self.original_username:
            user=User.query.filter_by(username=self.username.data).first
            if user is not None:
                raise ValidationError('Please use a different username')

class PostForm(FlaskForm):
    post=TextAreaField('Say something',validators=[DataRequired(),Length(0,1024)])
    submit=SubmitField('Submit')

class RestPasswordRequestForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    submit=SubmitField('Request Password Reset')

class RestPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    password2=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Request Password Reset')