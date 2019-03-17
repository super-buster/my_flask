# -*- coding: utf-8 -*-
from app import db,creat_app,cli
from app.models import User,Post


app= creat_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post)
