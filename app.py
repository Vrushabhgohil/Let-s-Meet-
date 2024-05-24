import os
from flask import Flask, redirect, request
from flask_login import LoginManager
from common.database import db
from common.model import User
from tenants.admin.api import admin_api 
from tenants.user.api import user_api 
from tenants.post.api import post_api 

def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'vrushabh@_2611'
   
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(user_api)
    app.register_blueprint(admin_api)
    app.register_blueprint(post_api)
    return app


app=create_app()
login_manager = LoginManager()
login_manager.init_app(app) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def add_photo(file):
    photos_path = os.path.join(os.getcwd(), 'static', 'photos')
    UPLOAD_FOLDER = photos_path
    folder = app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    filename = file.filename
    file.save(os.path.join(folder, filename))

@app.before_request
def before_request():
    tenant = request.headers.get('tenant')
    if tenant:
        db.choose_tenant(tenant)
        db.create_all()

@app.route('/')
def home():
    return redirect('login')
   
if __name__ == '__main__':
    app.run(debug=True)