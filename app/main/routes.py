# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template,redirect,url_for,flash,request,g, \
    jsonify,current_app,abort
from flask_login import current_user,login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm,PostForm,CommentForm
from app.models import User,Post,Permission,Role,Comment
from app.translate import translate
from app.main import bp
#动态获取用户登录的最后时间
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.utcnow()
        db.session.commit()
    g.__local=str(get_locale())

@bp.route('/',methods=['GET','POST'])
@bp.route('/index',methods=['GET','POST'])
@login_required
def index():
    form=PostForm()
    if form.validate_on_submit():
        language=guess_language(form.post.data)
        if language=='UNKNOWN' or len(language)>5:
            language=''
        post=Post(body=form.post.data,author=current_user,language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('You post is now live!'))
        return redirect(url_for('main.index'))
    page=request.args.get('page',1,type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url=url_for('main.index',page=posts.next_num) if posts.has_next else None
    prev_url=url_for('main.index',page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home page', form=form, posts=posts.items,
                           next_url=next_url,prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user=User.query.filter_by(username=username).first_or_404()
    page=request.args.get('page',1,type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url=url_for('main.user',username=username,page=posts.next_num) if posts.has_next else None
    prev_url=url_for('main.user',username=username,page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html',user=user,posts=posts.items,next_url=next_url,prev_url=prev_url)

@bp.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(_('You changes have been saved'))
        return redirect(url_for('main.edit_profile'))
    elif request.method  == 'GET':
        form.username.data=current_user.username
        form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',title='Edit Profile',form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s is not found.',username=username))
        return redirect(url_for('main.index'))
    if user==current_user:
        flash(_('You can not follow yourself!'))
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user',username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.',username=username))
        return redirect(url_for('main.index'))
    if user==current_user:
        flash(_('You cannot unfollow youself!'))
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.',username=username))
    return redirect(url_for('main.user',username=username))


@bp.route('/articles/')
def articles():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('main.articles', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.articles', page=posts.prev_num) if posts.has_prev else None
    return  render_template('explore.html',posts=posts.items,next_url=next_url,prev_url=prev_url)


@bp.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.body=form.post.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been rewrited')
        return redirect(url_for('main.articles',id=post.id))
    form.post.data=post.body
    return render_template('edit_post.html',form=form)

@bp.route('/article/<int:id>',methods=['GET','POST'])
@login_required
def article(id):
    form=CommentForm()
    p = Post.query.get_or_404(id)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=p,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('main.article',id=id))
    return render_template('post.html',p=p,id=id,form=form)

@bp.route('/article/delete/<int:id>',methods=['POST','GET','DELETE'])
def article_delete(id):
    post=Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    for comment in post.comments:
        db.session.delete(comment)
        db.session.commit()
    flash('the blog and comments have been deleted')
    return redirect(url_for('main.articles'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

@bp.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed'