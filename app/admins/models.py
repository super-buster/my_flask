# -*- coding: utf-8 -*-
from flask_login import current_user,login_required
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView,expose
from flask import redirect,url_for,flash
from flask_babel import _

class MyModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated
        )   #not method now!!

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.is_administrator():
            return super(MyAdminIndexView, self).index()
        else:
            flash(_('YOU CAN NOT DO THAT!'))
            return redirect(url_for('main.index'))

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