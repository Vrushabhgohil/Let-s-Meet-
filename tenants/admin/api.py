from flask import Blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


admin_api = Blueprint('admin_api', __name__,
                     template_folder='templates', static_folder='static')
engine = create_engine(
    'postgresql://postgres:postgres@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()