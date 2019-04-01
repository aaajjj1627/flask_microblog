#encoding:utf-8
from app import app,db
from flask import render_template,flash,redirect,url_for
from flask_login import current_user, login_user
from app.forms import LoginForm,EditProfileForm,ResetPasswordRequestForm,ResetPasswordForm
from app.models import User,Post
from flask_login import logout_user
from flask import request,g
from werkzeug.urls import url_parse
from app.forms import RegistrationForm,PostForm
from flask_login import login_required
from datetime import datetime
from app.email import send_password_reset_email,send_email
from werkzeug.urls import url_parse
from flask_babel import _,get_locale


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        '''
        _()函数将文本包装在基本语言中（本例是英语）。这个函数将使用由localeselector函数装饰选择的最佳语言 去为一个给定客户端查找正确的翻译。_()接着返回已翻译的文本，
         在这种情况下，将变成参数给flash()。
        '''
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    #User类的followed_posts方法返回一个SQLAlchemy查询对象，该对象被配置为从数据库中获取用户感兴趣的用户动态
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index',page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index',page = posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Home', form=form,
                           posts=posts.items,next_url=next_url,
                           prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # 重定向到 next 页面
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#记录上次访问的时间
@app.before_request
def before_request():
    g.locale = 'zh_CN'
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
'''
如果validate_on_submit()返回True，我将表单中的数据复制到用户对象中，然后将对象写入数据库。
GET请求，我需要通过提供表单模板的初始版本来响应
'''


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()#没有结果的情况下会自动发送404 error给客户端
    page = request.args.get('page', 1, type=int)
    # User类的followed_posts方法返回一个SQLAlchemy查询对象，该对象被配置为从数据库中获取用户感兴趣的用户动态
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user',username=user.username,page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

'''
如果用户名和密码都是正确的，那么我调用来自Flask-Login的login_user()函数。
该函数会将用户登录状态注册为已登录，这意味着用户导航到任何未来的页面时，应用都会将用户实例赋值给current_user变量。
'''

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        #动态组件，这个组件插入到静态文本的中间。_()函数有支持这类文本的语法，但它是基于较旧的字符串替换语法
        #flash('User {} not found.'.format(username))
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)!',username=username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username).',username=username))
    return redirect(url_for('user', username=username))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


