# db.py
from flask_sqlalchemy import SQLAlchemy
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOCAL_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'profiles.db')

db = SQLAlchemy()
