from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from flask import redirect, request, url_for
from common.database import db
from common.model import Post, Post_comment, Post_like
from sqlalchemy import desc

def all_post():
    posts = Post.query.order_by(desc(Post.post_date)).all()
    return posts

def users_post(user):
    posts = Post.query.order_by(desc(Post.post_date)).filter(Post.post_by==user).all()
    return posts

def comments(post,user):
    comment = Post_comment.query.order_by(desc(Post_comment.post_comment_date)).filter(Post_comment.post_comment_by==user).all()
    return comment

def newpost(user):
    post_id = str(uuid.uuid4())
    post_addr = request.files.get("post_addr")
    post_by = user.id
    post_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    post_caption = request.form.get('caption')
    post_mention = request.form.get('mention')
    if post_addr:
        img_filename = secure_filename(post_addr.filename)
        post_addr.save(os.path.join(
            'E:/vrushabh/python_project/static', img_filename))
        try:
            add_post = Post(post_id=post_id, post_addr=img_filename if post_addr else None,post_by=post_by,
                            post_date=post_date, post_caption=post_caption, post_mention=post_mention)
            db.session.add(add_post)
            db.session.commit()
            user.post += 1
            db.session.commit()
            return redirect(url_for('user_api.home', tenant=user.name))
        except Exception as e :
            print(e)
    else:
        img_filename = None
    return redirect(url_for('user_api.home', tenant=user.name))



def like_current_post(post_id,user):
    fnd_post = Post.query.get(post_id)
    if fnd_post:
        fnd_post.post_like += 1
        db.session.commit()    
        add_like = Post_like(
            post_like_id = str(uuid.uuid4()),
            post_id = post_id,
            post_like_by = user
        )
        db.session.add(add_like)
        db.session.commit()

def dislike_current_post(post_id,user):
    fnd_post = Post.query.get(post_id)
    if fnd_post:
        fnd_post.post_like -= 1
        remove_like = Post_like.query.filter(Post_like.post_id==post_id,Post_like.post_like_by==user).first()
        db.session.delete(remove_like)
        db.session.commit() 

def delete_current_post(post_id,user):
    fnd_post = Post.query.get(post_id)
    if fnd_post:
        delete_like = Post_like.query.filter(Post_like.post_id==post_id).first()
        if delete_like:
            db.session.delete(delete_like)
            db.session.commit() 
                
        db.session.delete(fnd_post)
        db.session.commit() 
        user.post -=1
        db.session.commit() 


def comment_current_post(post_id,user):
    post_comment_id = str(uuid.uuid4()),
    post_content = request.form.get("post_content")
    
    add_comment = Post_comment(post_comment_id=post_comment_id,post_id=post_id,post_comment_by=user,post_content=post_content)
    db.session.add(add_comment)
    db.session.commit()

def remove_commnet_current_post(post_id,user):
    comment = Post_comment.query.filter(Post_comment.post_id==post_id,Post_comment.post_comment_by==user).first()
    comment.post_comment_status = "Deleted"
    db.session.commit()