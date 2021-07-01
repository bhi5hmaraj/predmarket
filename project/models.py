from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
# import pytz
#base = declarative_base()

#class User(base):
#	__tablename__ = "users"
#

from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(Integer, primary_key=True)
    fb_user_id = db.Column(String)
    credits = db.Column(Float)
    email_id = db.Column(String)

    def get_id(self):
        return self.user_id
'''    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))
    credits = db.Column(db.Float)
'''
class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(10000))
    explanation_text = db.Column(db.String(10000))
    resolution_rule_text = db.Column(db.String(10000))
    deadline_for_betting = db.Column(db.DateTime) # .astimezone(pytz.timezone('Asia/Kolkata'))
    deadline_for_resolving = db.Column(db.DateTime) # .astimezone(pytz.timezone('Asia/Kolkata'))
    is_active = db.Column(db.Boolean)

class Options(db.Model):
    option_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer)
    price = db.Column(db.Float)
    option_text = db.Column(db.String(1000))
    num_of_outstanding_shares = db.Column(db.Integer)

class user_portfolios(db.Model):
    user_id = db.Column(db.Integer,primary_key=True)
    num_shares = db.Column(db.Integer,primary_key=True)
    option_id = db.Column(db.Integer)
