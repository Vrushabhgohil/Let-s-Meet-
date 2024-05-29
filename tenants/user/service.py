from datetime import datetime
import os
import uuid
from flask_login import current_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from flask import render_template, request
import jwt
from common.database import db
from common.model import Notification, User
from sqlalchemy import text
from tenants.post.service import common_notification

def all_user():
    users = User.query.all()
    return users

def users_notification(user):
    newmsg = Notification.query.order_by(desc(Notification.notification_date)).filter(Notification.notification_to == user,Notification.notification_status == True).all()
    return newmsg

def dismiss_a_note(notification_id):
    fnd_note = Notification.query.filter(Notification.notification_id == notification_id).first()
    fnd_note.notification_status = False
    fnd_note.change_at = datetime.now()
    db.session.commit()

def dismiss_all_note():
    newmsg = Notification.query.filter(Notification.notification_to == current_user.name,Notification.notification_status == True).all()
    for i in newmsg:
        i.notification_status = False
        i.change_at = datetime.now()
        db.session.commit()
    return render_template('user/notification.html',tenant=current_user.name)


def signup_user():
    try:
        id = str(uuid.uuid4())
        name = request.form.get("name")
        username = request.form.get("username")
        dp_addr_file = request.files.get("dp_addr_file")
        email = request.form.get("email")
        password = request.form.get("password")
        payload = {'password': password}
        created_at = datetime.now()
        updated_at = None
        token = jwt.encode(payload, 'vrushabh@2611', algorithm='HS256')
        new_passwrod = token
        filename = None
        if dp_addr_file:
            filename = secure_filename(dp_addr_file.filename)
            dp_addr_file.save(os.path.join('E:\\vrushabh\python_project\static',filename))

        add_user = User(id=id,name=name,username=username,dp_addr=filename,email=email,password = new_passwrod,created_at=created_at,updated_at=updated_at)
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

def Searchresult(session,user,search):
    all_users = User.query.filter(User.name != current_user.name).all()
    search_used = session.execute(text(f'SELECT * FROM "myschema"."User" WHERE LOWER(name) LIKE :values'),
            {"values": f"%{search.lower()}%"}).fetchall()
    return render_template('user/search.html',all_users=all_users,search_result=search_used,tenant=user)


def Update_user_details(one_user):
    username = request.form.get('username')
    email = request.form.get('email')
    dpimg = request.files.get('dpimg')
    filename = one_user.dp_addr
    updated_at =datetime.now()
    if dpimg:
        filename = secure_filename(dpimg.filename)
        filepath = os.path.join('E:\\vrushabh\\python_project\\static', filename)
        dpimg.save(filepath)

    one_user.dp_addr = filename
    one_user.username = username
    one_user.email = email
    one_user.updated_at = updated_at
    db.session.commit()

    
def add_notification(user,tenant):
    note_details = f"{user} Request to Follow You, Do You Want To Follow Them ?",
    note_on = f"User Follow",
    common_data = common_notification(user,tenant)
    if common_data.notification_to != common_data.notification_from:    
        new_notification = Notification(notification_details=note_details,notification_on=note_on,**common_data)
        db.session.add(new_notification)
        db.session.commit()
