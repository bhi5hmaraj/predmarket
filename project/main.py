from flask import Blueprint, render_template, request, session, redirect
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

def getTableByQuestionIdx(tablename,idx):
	text = 'SELECT * FROM '+tablename+' WHERE question_id = '+ str(idx) 
	questions = db.session.execute(text).fetchall()
	return questions

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    questions = getTable('Questions')
    if request.method == 'POST':
        req = request.form.to_dict()
        session['questionIdx']=req['qId']
        return redirect('/questionMarket')

    # return render_template('profile.html', user=current_user, questions=list(map(changeTZ,  questions)))
    return render_template('profile.html', user=current_user, questions=questions)

@main.route('/questionMarket',methods=['GET','POST'])
@login_required
def questionMarket():
	questionIdx = session['questionIdx']
	question = getTableByQuestionIdx('Questions', questionIdx)
	options = getTableByQuestionIdx('Options', questionIdx)
	if request.method == 'POST':
		req = request.form.to_dict()
		kafkaDict = {}
		for key in req:
			if 'option_' in key:
				kafkaDict['option_id'] = key[key.index('_')+1:]
				kafkaDict['numShares'] = req[key]
		kafkaDict['user_id'] = current_user.user_id
		kafkaDict['question_id'] = questionIdx
		kafkaDict['isBuy'] = req["isBuy-button"] == 'True'
	return render_template('questionMarket.html',user=current_user,question=question,options=options)





