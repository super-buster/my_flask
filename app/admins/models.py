# -*- coding: utf-8 -*-
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated  #not attribute now!! you can not use is_authenticated()


class UserModelView(ModelView):
    page_size = 50
    create_modal = True
    edit_modal = True
    can_export = True
    column_exclude_list = ['password_hash' ]
    column_searchable_list = ['username', 'email','about_me']

class PostModelView(ModelView):
    column_searchable_list = ['body']
    create_modal = True
    edit_modal = True
    can_export = True

class CommentModelView(ModelView):
    column_searchable_list = ['body']
    create_modal = True
    edit_modal = True
    can_export = True