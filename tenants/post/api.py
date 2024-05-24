from datetime import datetime
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.database import switch_tenant
from common.model import Post
from tenants.post.service import archivepost, comment_current_post
from tenants.post.service import delete_current_post, dislike_current_post, like_current_post, newpost, remove_commnet_current_post
from common.database import db

post_api = Blueprint('post_api', __name__,template_folder='templates', static_folder='static')
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()

@post_api.route('/post_image/<string:tenant>', methods=['GET', 'POST'])
@login_required
@switch_tenant
def post_image(tenant):
    user = current_user
    newpost(user)
    return render_template('user/add_post.html', user=user, schema = tenant)

@post_api.route('/editpost/<string:post_id>',methods=['GET','POST'])
@login_required
def edit_post(post_id):
    one_post = Post.query.filter(Post.post_id==post_id).first()
    if request.method == 'POST':
        caption = request.form.get('caption')
        mention = request.form.get('mention')
        updated_at = datetime.now()
        one_post.post_caption = caption
        one_post.post_mention = mention  
        one_post.updated_at = updated_at
        db.session.commit()

        return redirect(url_for('user_api.home',tenant =current_user.name))
    return render_template('user/edit_post.html',one_post=one_post)

@post_api.route('/archive_post/<string:post_id>', methods=['POST'])
def archive_post(post_id):
    user = current_user 
    archivepost(post_id)
    return redirect(url_for('user_api.home', tenant=user.name))

@post_api.route('/delete_post/<string:post_id>', methods=['POST'])
def delete_post(post_id):
    user = current_user 
    delete_current_post(post_id,user)
    return redirect(url_for('user_api.home', tenant=user.name))

@post_api.route('/like_post/<string:post_id>', methods=['POST'])
def like_post(post_id):
    user = current_user
    like_current_post(post_id,user)
    return redirect(url_for('user_api.home', tenant=user.name))

@post_api.route('/add_comment/<string:post_id>', methods=['POST'])
def add_comment(post_id):
    user = current_user
    comment_current_post(post_id,user.id)
    return redirect(url_for('user_api.home', tenant=user.name))

@post_api.route('/delete__comment/<string:post_id>', methods=['POST'])
def delete__comment(post_id):
    user = current_user
    remove_commnet_current_post(post_id,user.id)
    return redirect(url_for('user_api.home', tenant=user.name))

@post_api.route('/dislike_post/<string:post_id>', methods=['POST'])
def dislike_post(post_id):
    user = current_user
    dislike_current_post(post_id,user.id)
    return redirect(url_for('user_api.home', tenant=user.name))


