from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from flask import redirect, request, url_for
from common.database import db
from common.model import Notification, Post, Post_comment, Post_like, User
from sqlalchemy import desc

def all_post():
    posts = Post.query.order_by(desc(Post.created_at)).filter(Post.post_status == True).all()
    return posts

def users_post(user):
    posts = Post.query.order_by(desc(Post.created_at)).filter(Post.post_by==user,Post.post_status==True).all()
    return posts

def permenent_delete():
    false_posts = Post.query.filter(Post.post_status == False).first()
    if false_posts:
        false_posts_like = Post_like.query.filter(Post_like.post_id == false_posts.post_id).all()
        current_time = datetime.now()
        time_diff = current_time - false_posts.updated_at
    
        if time_diff.total_seconds() > 86400: 
            for false_posts_likes in false_posts_like:
                db.session.delete(false_posts_likes) # delete all the post which is saved as archive from last one day
            db.session.delete(false_posts)

        db.session.commit()

# ADD NEW POST

def newpost(user):
    post_id = str(uuid.uuid4())
    post_addr = request.files.get("post_addr")
    post_by = user.id
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    post_caption = request.form.get('caption')
    post_mention = request.form.get('mention')
    created_at = datetime.now()
    updated_at = None
    if post_addr:
        img_filename = secure_filename(post_addr.filename)
        post_addr.save(os.path.join(
            'E:/vrushabh/python_project/static', img_filename))
        try:
            add_post = Post(post_id=post_id, post_addr=img_filename if post_addr else None,post_by=post_by,
                            created_at=created_at, post_caption=post_caption, post_mention=post_mention,updated_at=updated_at)
            db.session.add(add_post)
            db.session.commit()
            mention_notification(user.name,post_mention,post_id)
            user.post += 1
            db.session.commit() 
            return redirect(url_for('user_api.home', tenant=user.name))
        except Exception as e :
            print(e)
    else:
        img_filename = None


# NOTIFICATIONS FOR MENTION AND LIKE
def common_notification(user,muser):
    common_data = {
        'notification_id' : str(uuid.uuid4()),
        'notification_to' : muser,
        'notification_from' : user,
        'notification_date' : datetime.now(),
        'change_at' : None
    }

    return common_data

def mention_notification(user,muser,post_id):
    note_details = f"{user} Mentioned You In Thier Post",
    note_on = f"Post Mention :- {post_id}",
    common_data = common_notification(user,muser)
    new_notification = Notification(notification_details=note_details,notification_on=note_on,**common_data)
    db.session.add(new_notification)
    db.session.commit()

def likepost_notification(user,muser,post_id):
    note_details = f"{user} Liked Your Post",
    note_on = f"Post Like :- {post_id}",
    common_data = common_notification(user,muser)
    new_notification = Notification(notification_details=note_details,notification_on=note_on,**common_data)
    db.session.add(new_notification)
    db.session.commit()


# LIKE DISLIKE AND DELETE POST
def like_current_post(post_id,user):
    fnd_post = Post.query.get(post_id)
    if fnd_post:
        fnd_post.post_like += 1

        post_like_id = str(uuid.uuid4())
        post_like_by = user.id
        post_like_date = datetime.now()

        add_like = Post_like(post_like_id=post_like_id,post_id=post_id,post_like_by=post_like_by,post_like_date=post_like_date)
        getpost = Post.query.filter(Post.post_id==post_id).first()
        getuser = User.query.filter(User.id == getpost.post_by).first()
        
        if user.name != getuser.name:
            likepost_notification(user.name, getuser.name, post_id)
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
        fnd_post.post_status = False
        fnd_post.updated_at = datetime.now()
        user.post -= 1
        db.session.commit() 

def archivepost(post_id):
    fnd_post = Post.query.get(post_id)
    if fnd_post:
        fnd_post.post_status = False
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