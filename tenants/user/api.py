from flask import Blueprint, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.database import db, switch_tenant
from common.model import Post_like, User
from tenants.user.service import Searchresult, add_notification, all_post, all_user, authenticate, User_user, comments
from tenants.user.service import users_notification, users_post

user_api = Blueprint('user_api', __name__,
                     template_folder='templates', static_folder='static')
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()

@user_api.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            user = User_user()
            if user:
                schema = g.tenant = user.name
                db.choose_tenant(schema)
                session.add(user)
        except Exception as e:
            print(e)
    return redirect(url_for('user_api.login'))


@user_api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = authenticate()
        if user:
            login_user(user)
            user.is_active = True
            db.session.commit()
            return redirect(url_for('user_api.home', tenant=user.name))
        else:
            msg = 'Invalid Username or Password'
            return render_template('login.html', msg=msg)

    return render_template('login.html')

@user_api.route('/home/<string:tenant>')
@login_required
@switch_tenant
def home(tenant):
    tenant = current_user.name
    user = all_user()
    display_posts = all_post()
    like_status={}
    for i in display_posts:
        like_unlike_posts = Post_like.query.filter_by(post_id=i.post_id,post_like_by=current_user.id).first()
        like_status[i.post_id] = like_unlike_posts is not None

        post_comments = comments(i.post_id,current_user.id)
    return render_template('user/home.html',tenant=tenant,user=user,display_posts=display_posts,like_status=like_status,post_comments=post_comments)

@user_api.route('/profile/<string:tenant>')
@login_required
@switch_tenant      
def profile(tenant):
    schema = current_user.name
    post_data = User.query.filter(User.name == tenant).first()
    display_your_post = users_post(post_data.id)
    return render_template('user/profile.html', user=post_data, tenant=schema, display_your_post=display_your_post)


@user_api.route('/search/<string:tenant>', methods=['GET', 'POST'])
@login_required
@switch_tenant
def search_user(tenant):
    cuser= current_user.name
    users = all_user()
    search = request.form.get('search')
    if search:
        result = Searchresult(session,cuser,search)
        return result
    return render_template('user/search.html', all_users=users, tenant=cuser)


@user_api.route('/follow/<string:tenant>')
@login_required
def follow(tenant):
    user = current_user.name
    send_notification = add_notification(user,tenant)
    return redirect(url_for('user_api.profile', tenant=tenant))

@user_api.route('/notifications/<string:tenant>',methods=['GET','POST'])
def notifications(tenant):
    user = current_user.name
    newnote = users_notification(user)
    return render_template('user/notification.html',tenant=user,newnote=newnote)

@user_api.route('/logout')
@login_required
def logout():
    user = current_user
    user.is_active = False
    db.session.commit()
    logout_user()
    return redirect(url_for('user_api.login'))