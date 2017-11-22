# _*_coding:utf-8_*_
from flask import render_template, flash, redirect, url_for, abort, current_app, request, make_response
from datetime import datetime
from . import main
from ..models import User, db, Role, Permission, Post, Comment
from flask_login import current_user, login_required
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        # 其实Permission这里是多余的，因为如果没有写文章权限 index.html不会显示表单，form.validate_on_submit也无从谈起了
        myart = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(myart)
        return redirect(url_for('.index'))
    # myarts = Post.query.order_by(Post.timestamp.desc()).all()
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed'))
    if show_followed:
        query123 = current_user.followed_posts
    else:
        query123 = Post.query
    page = request.args.get('page', 1, type=int)
    # pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=True)
    # if page > pagination.pages:
    #     page = pagination.pages
    #     pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
    #         page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #       error_out=True)
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    if page > (query123.count() - 1) / per_page + 1:
        page = (query123.count() - 1) / per_page + 1
    pagination = query123.order_by(Post.timestamp.desc()).paginate(
        page, per_page)
    posts = pagination.items
    return render_template('index.html', current_time=datetime.utcnow(), form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE']
    if page > (Comment.query.count() - 1) / per_page + 1:
        page = (Comment.query.count() - 1) / per_page + 1
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


@main.route('/moderate_enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate_disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/user/<username>')
def user(username):
    user123 = User.query.filter_by(username=username).first()
    if user123 is None:
        abort(404)
    # myarts = user123.posts.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    if page > (Post.query.count() - 1) / per_page + 1:
        page = (Post.query.count() - 1) / per_page + 1
    pagination = user123.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page)
    posts = pagination.items
    return render_template('user.html', user=user123, posts=posts, pagination=pagination)


@main.route('/follow/<username>')
@permission_required(Permission.FOLLOW)
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE']
    if page > (user.followers.count() - 1)/per_page + 1:
        page = (user.followers.count() - 1)//per_page + 1
    pagination = user.followers.paginate(page, per_page)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="followers of", endpoint='.followers',
                           pagination=pagination, follows=follows)


@main.route('/followeds/<username>')
def followeds(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_FOLLOWEDS_PER_PAGE']
    if page > (user.followeds.count() - 1) / per_page + 1:
        page = (user.followeds.count() - 1) / per_page + 1
    pagination = user.followeds.paginate(page, per_page)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followeds.html', user=user, title="followeds of", endpoint='.followeds',
                           pagination=pagination, follows=follows)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          author_id= current_user._get_current_object().id,
                          post_id=post.id)
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE']
    if page == -1 or page > ((post.comments.count() - 1) / per_page + 1):
        page = (post.comments.count() - 1) / per_page + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)  # 这里提交的还是post 不是post.id
        flash('The post has been updated')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', abc=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user111 = User.query.get_or_404(id)
    form = EditProfileAdminForm(user111)  # user456=user also ok because location parameter
    if form.validate_on_submit():
        user111.email = form.email.data
        user111.username = form.username.data
        user111.role = Role.query.get(form.role.data)  # Role.query.filter_by(id=form.role.data).first()
        user111.name = form.name.data
        user111.location = form.location.data
        user111.about_me = form.about_me.data
        db.session.add(user111)
        flash("The profile has benn updated.")
        return redirect(url_for('.user', username=user111.username))
    form.email.data = user111.email
    form.username.data = user111.username
    form.role.data = user111.role_id
    form.name.data = user111.name
    form.location.data = user111.location
    form.about_me.data = user111.about_me
    return render_template('edit_profile.html', abc=form)
