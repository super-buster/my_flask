# -*- coding: utf-8 -*-
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView,expose
from flask import redirect,url_for

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  #not method now!!

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return super(MyAdminIndexView, self).index()


class UserModelView(MyModelView,ModelView):
    page_size = 50
    create_modal = True
    edit_modal = True
    can_export = True
    column_exclude_list = ['password_hash' ]
    column_searchable_list = ['username', 'email','about_me']

class PostModelView(MyModelView,ModelView):
    column_searchable_list = ['body','title']
    create_modal = True
    edit_modal = True
    can_export = True

class CommentModelView(MyModelView,ModelView):
    column_searchable_list = ['body']
    create_modal = True
    edit_modal = True
    can_export = True