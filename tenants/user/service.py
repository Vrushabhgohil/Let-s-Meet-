from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from flask import redirect, render_template, request, url_for
import jwt
from common.database import db
from common.model import Post, Post_comment, Post_like, User
from sqlalchemy import desc,text

def all_user():
    users = User.query.all()
    return users

def all_post():
    posts = Post.query.order_by(desc(Post.post_date)).all()
    return posts

def users_post(user):
    posts = Post.query.order_by(desc(Post.post_date)).filter(Post.post_by==user).all()
    return posts

def comments(post,user):
    comment = Post_comment.query.order_by(desc(Post_comment.post_comment_date)).filter(Post_comment.post_comment_by==user).all()
    return comment

def User_user():
    try:
        id = str(uuid.uuid4())
        name = request.form.get("name")
        username = request.form.get("username")
        dp_addr_file = request.files.get("dp_addr_file")
        email = request.form.get("email")
        password = request.form.get("password")
        payload = {'password': password}
        token = jwt.encode(payload, 'vrushabh@2611', algorithm='HS256')
        new_passwrod = token

        filename = None
        if dp_addr_file:
            filename = secure_filename(dp_addr_file.filename)
            dp_addr_file.save(os.path.join('E:\\vrushabh\python_project\static',filename))

        add_user = User(id=id,name=name,username=username,dp_addr=filename,email=email,password = new_passwrod)
        db.session.add(add_user)
        db.session.commit()
        return add_user

    except Exception as e:
        print(e)

def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        try:
            token = user.password
            new_password = jwt.decode(
                token, 'vrushabh@2611', algorithms='HS256')
            if user and new_password['password'] == password:
                return user
        except jwt.DecodeError:
            pass
    return None

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


def Searchresult(session,user,search):
    all_users =all_user()
    search_used = session.execute(text(f'SELECT * FROM "myschema"."User" WHERE LOWER(name) LIKE :values'),
            {"values": f"%{search.lower()}%"}).fetchall()
    return render_template('user/search.html',all_users=all_users,search_result=search_used,tenant=user)

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