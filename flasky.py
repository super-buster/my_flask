from app import app,db,manage
from app.models import User,Post
from flask_script import  Shell

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post)
manage.add_command("shell",Shell(make_context=make_shell_context))

if __name__ == '__main__':
    app.run(debug=True)