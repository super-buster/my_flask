# -*- coding: utf-8 -*-
from flask import request
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import  DataRequired, ValidationError,Length,Regexp
from flask_babel import _,lazy_gettext as _l
from app.models import  User

class EditProfileForm(FlaskForm):
    username=StringField(_l('Username'),validators=[
            DataRequired(),Length(1,64),Regexp(r'^[a-zA-Z]+[a-zA-Z0-9_.]*$',0,
                                               'Usernames must have only letters,'
                                                'numbers ,dots or underscores')])
    about_me=TextAreaField(_l('About me'),validators=[Length(0,1024)])
    submit=SubmitField(_l('Submit'))

    #继承Flask的__init__方法
    def __init__(self,original_username,*args,**kwargs):
        super(EditProfileForm, self).__init__(*args,**kwargs)
        self.original_username=original_username

    def validate_username(self,username):
        if username.data!=self.original_username:
            user=User.query.filter_by(username=self.username.data).first
            if user is not None:
                raise ValidationError(_('Please use a different username'))

class PostForm(FlaskForm):
    post=PageDownField(_l("What's your mind? (markdown support)"),validators=[DataRequired()])
    submit=SubmitField(_l('Submit'))

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)