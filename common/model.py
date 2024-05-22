from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey,Integer, String
from common.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    __table_args__ = {'schema': 'myschema'}
    id = Column(String(100), primary_key=True)
    name = Column(String(250), nullable=False)
    username = Column(String(250), unique=True, nullable=False)
    dp_addr = Column(String(250),nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(250), nullable=False)
    following = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    post = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    is_superadmin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    __tablename__ = 'Post'
    __table_args__ = {'schema': 'myschema'}
    post_id = Column(String(100), primary_key=True)
    post_addr = Column(String(500), nullable=False)
    post_by =Column(String(50),ForeignKey('myschema.User.id'),nullable=False)
    post_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    post_caption = Column(String(250))
    post_mention = Column(String(250))
    post_like = Column(Integer, default=0)  
    post_comment = Column(Integer, default=0)
    post_status = Column(Boolean,default=True)

    user = db.relationship('User',primaryjoin=(User.id == post_by))


class Post_like(db.Model):
    __tablename__ = 'Post_like'
    __table_args__ = {'schema': 'myschema'}
    post_like_id = Column(String(100), primary_key=True)
    post_id = Column(String(50),ForeignKey('myschema.Post.post_id') , nullable=False)
    post_like_by = Column(String(50),ForeignKey('myschema.User.id'), nullable=False)
    post_like_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User',primaryjoin=(User.id == post_like_by))
    post = db.relationship('Post',primaryjoin=(Post.post_id == post_id))

class Post_comment(db.Model):
    __tablename__ = 'Post_comment'
    __table_args__ = {'schema': 'myschema'}
    post_comment_id = Column(String(100), primary_key=True)
    post_id = Column(String(50),ForeignKey('myschema.Post.post_id') , nullable=False)
    post_comment_by = Column(String(30),ForeignKey('myschema.User.id'), nullable=False)
    post_content = Column(String(200),nullable=False)
    post_comment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    post_comment_like = Column(Integer,default=0)
    post_comment_status = Column(String(10),default="published")
    user = db.relationship('User',primaryjoin=(User.id == post_comment_by))
    post = db.relationship('Post',primaryjoin=(Post.post_id == post_id))


class Notification(db.Model):
    __tablename__ = 'Notification'
    notification_id = Column(String(100), primary_key=True)
    notification_details = Column(String(250), nullable=False)
    notification_type = Column(String(50), unique=False)
    notification_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notification_status = Column(String(30),nullable=True)
