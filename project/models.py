from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
# import pytz
#base = declarative_base()

#class User(base):
#       __tablename__ = "users"
#

from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(Integer, primary_key=True)
    fb_user_id = db.Column(String)
    password = db.Column(db.String(100))
    credits = db.Column(Float)
    email_id = db.Column(String)

    def get_id(self):
        return self.user_id

class Questions(db.Model):
    
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(10000))
    explanation_text = db.Column(db.String(10000))
    resolution_rule_text = db.Column(db.String(10000))
    deadline_for_betting = db.Column(db.DateTime) # .astimezone(pytz.timezone('Asia/Kolkata'))
    deadline_for_resolving = db.Column(db.DateTime) # .astimezone(pytz.timezone('Asia/Kolkata'))

class Options(db.Model):
    option_id = db.Column(db.Integer, primary_key=True) 
    question_id = db.Column(db.Integer)                 
    price = db.Column(db.Float)        
    option_text = db.Column(db.String(1000)) 
    num_of_outstanding_shares = db.Column(db.Integer)      