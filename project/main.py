from flask import Blueprint, render_template
from . import db
from flask_login import login_required, current_user
import pytz

def changeTZ(og_question):
    question = dict(og_question)
    question['deadline_for_betting'] = question['deadline_for_betting'].astimezone(pytz.timezone('Asia/Kolkata')).strftime("%B %d %Y, %I:%M:%S %p")
    question['deadline_for_resolving'] = question['deadline_for_resolving'].astimezone(pytz.timezone('Asia/Kolkata')).strftime("%B %d %Y, %I:%M:%S %p")
    return question

def getTable(tablename):
    text = 'SELECT * FROM '+tablename
    questions = db.session.execute(text).fetchall()
    return questions

main = Blueprint('main', __name__)

...
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    questions = getTable('Questions')
    return render_template('profile.html', user=current_user, questions=list(map(changeTZ,  questions)))
    #return render_template('profile.html', name=current_user.fb_user_id,credits=current_user.credits)

@main.route('/questionMarket')
@login_required
def questionMarket():
    return render_template('questionMarket.html')