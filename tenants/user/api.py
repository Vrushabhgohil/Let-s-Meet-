from datetime import timedelta
from flask import Blueprint, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.database import db, switch_tenant
from common.model import Post_like, User
from tenants.post.service import all_post, permenent_delete, users_post
from tenants.user.service import (
    Searchresult, Update_user_details, add_notification, all_user, authenticate,
    dismiss_a_note, dismiss_all_note, signup_user, users_notification
)
user_api = Blueprint('user_api', __name__,
                     template_folder='templates', static_folder='static')
engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()


@user_api.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            user = signup_user()
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
            login_user(user,remember=True,duration=timedelta(days=1)) #it remeber user for one dayy
            user.is_active = True
            db.session.commit()
            return redirect(url_for('user_api.home', tenant=user.name))
        else:
            return render_template('login.html', msg='Invalid Username or Password')
    return render_template('login.html')


@user_api.route('/home/<string:tenant>')
@login_required
@switch_tenant
def home(tenant):
    tenant = current_user.name
    user = all_user()
    display_posts = all_post()
    like_status = {post.post_id: Post_like.query.filter_by(
        post_id=post.post_id, post_like_by=current_user.id).first() is not None for post in display_posts}
    permenent_delete()
    return render_template('user/home.html', tenant=tenant, user=user, display_posts=display_posts, like_status=like_status)


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
    cuser = current_user.name
    users = User.query.filter(User.name != current_user.name).all()
    search = request.form.get('search')
    if search:
        return Searchresult(session, cuser, search)
    return render_template('user/search.html', all_users=users, tenant=cuser)


@user_api.route('/follow/<string:tenant>')
@login_required
def follow(tenant):
    add_notification(current_user.name, tenant)
    return redirect(url_for('user_api.profile', tenant=tenant))


@user_api.route('/notifications/<string:tenant>', methods=['GET', 'POST'])
@login_required
def notifications(tenant):
    newnote = users_notification(current_user.name)
    return render_template('user/notification.html', tenant=current_user.name, newnote=newnote)


@user_api.route('/dismissnote/<string:notification_id>')
@login_required
def dismissnote(notification_id):
    dismiss_a_note(notification_id)
    return redirect(url_for('user_api.notifications', tenant=current_user.name))


@user_api.route('/dismissallnote')
@login_required
def dismissallnote():
    dismiss_all_note()
    return redirect(url_for('user_api.notifications', tenant=current_user.name))


@user_api.route('/editprofile/<string:tenant>', methods=['GET', 'POST'])
@login_required
def editprofile(tenant):
    one_user = User.query.filter(User.name == tenant).first()
    if request.method == 'POST':
        Update_user_details(one_user)
        return redirect(url_for('user_api.home', tenant=current_user.name))
    return render_template('user/edit_profile.html', one_user=one_user)


@user_api.route('/logout')
@login_required
def logout():
    current_user.is_active = False
    db.session.commit()
    logout_user()
    return redirect(url_for('user_api.login'))
