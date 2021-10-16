from flask import Blueprint, render_template, request, session, redirect, jsonify
from . import db
from flask_login import login_required, current_user
import pytz
import string
import random
from kafka import KafkaProducer
import json
from kafka import KafkaConsumer
import threading
import numpy as np

def changeTZ(og_question):
    question = dict(og_question)
    question['deadline_for_betting'] = question['deadline_for_betting'].astimezone(pytz.timezone('Asia/Kolkata')).strftime("%B %d %Y, %I:%M:%S %p")
    question['deadline_for_resolving'] = question['deadline_for_resolving'].astimezone(pytz.timezone('Asia/Kolkata')).strftime("%B %d %Y, %I:%M:%S %p")
    return question

def getTable(tablename):
    text = 'SELECT * FROM '+tablename
    questions = db.session.execute(text).fetchall()
    return questions

def getOptionByOptionId(id):
    query='SELECT * FROM OPTIONS WHERE option_id='+str(id)
    options=db.session.execute(query).fetchall()
    return options

def getQuestionData(q_id):
    query='SELECT * FROM OPTIONS WHERE QUESTION_ID='+str(q_id)
    options=db.session.execute(query).fetchall()
    return options

def getTableByQuestionIdx(tablename,idx):
    text = 'SELECT * FROM '+tablename+' WHERE question_id = '+ str(idx) 
    questions = db.session.execute(text).fetchall()
    return questions

def getPortfolioByUserIdx(idx):
	text = 'SELECT * FROM user_portfolios WHERE user_id = '+ str(idx)
	portfolio = db.session.execute(text).fetchall()
	return portfolio

def getPortfolioByUidOid(user_id,option_id):
    text = 'SELECT num_shares FROM user_portfolios WHERE user_id = '+ str(user_id)+' AND option_id = '+str(option_id)
    stakes = db.session.execute(text).fetchall()
    return stakes

def get_active_questions(questions):
   active_questions = []
   for question in questions:
        if question['is_active']:
             active_questions.append(question)
   return active_questions

def calc_cost(options,kafka_dict=None):
   '''
   This function calculates the cost of a trade. If kakfa_dict is None then it calculates before the trade.
   '''
   if kafka_dict:
       for op in options:
           if op['option_id']==int(kafka_dict['option_id']):
               if kafka_dict['numShares'] == '':
                    kafka_dict['numShares'] = 0
               op['num_of_outstanding_shares'] += (1 if kafka_dict['isBuy'] else -1) * int(kafka_dict['numShares'])
#               op['num_of_outstanding_shares'] += int(kafka_dict['numShares'])
   num_outstanding = np.array([op['num_of_outstanding_shares'] for op in options])
   cost = B*np.log(np.sum(np.exp(num_outstanding/B)))
   return cost



def get_ranking():
    # text = 'SELECT U.user_id,  pscore , fb_user_id from users U INNER JOIN (SELECT user_id, sum(net_gain) as pscore from gains GROUP BY user_id) R ON U.user_id=R.user_id ORDER BY pscore'
    text = 'SELECT U.user_id,  pscore , fb_user_id, ROW_NUMBER () OVER (ORDER BY pscore) as rank from users U INNER JOIN (SELECT user_id, sum(net_gain) as pscore from gains GROUP BY user_id) R ON U.user_id=R.user_id'
    ranking = db.session.execute(text).fetchall()
    return roundoff_scores(ranking)

def roundoff_scores(ranking):
    ranking = list(map(lambda r: dict(r), ranking))
    for r in ranking: 
        r['pscore'] = round(r['pscore'], 3)
    return ranking

COST_SCALING_FACTOR = 100
B = 10

main = Blueprint('main', __name__)

...
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    questions = getTable('Questions')
    active_questions = get_active_questions(questions)
    ranking = get_ranking()
    if request.method == 'POST':
        req = request.form.to_dict()
        session['questionIdx'] = req['qId']
        return redirect('/questionMarket')
    return render_template('profile.html', user=current_user, questions=list(map(changeTZ,  active_questions)),ranking=ranking)
    #return render_template('profile.html', name=current_user.fb_user_id,credits=current_user.credits)

# https://stackoverflow.com/questions/53263393/is-there-a-python-api-for-event-driven-kafka-consumer/53267676#53267676
def register_kafka_listener(transaction_id):
    # Poll kafka

    consumer = KafkaConsumer('transactions-out',bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest')

    for msg in consumer:
        y = json.loads(msg.value)
        if y['transaction_id'] == transaction_id:
            return y['status']
    return False

def row_to_dict(row):
    dict = [{column: value for column, value in rowproxy.items()} for rowproxy in row]
    return dict

@main.route('/questionMarket',methods=['GET','POST'])
@login_required
def questionMarket():
    questionIdx = session['questionIdx']
    question = getTableByQuestionIdx('Questions', questionIdx)
    options = getTableByQuestionIdx('Options', questionIdx)
    options = row_to_dict(options)

    for op in options:
        stake = row_to_dict(getPortfolioByUidOid(current_user.user_id,op['option_id']))
        try:
            op['stake'] = stake[0]['num_shares']
        except:
            op['stake'] = 0
        op['op'] = op['price']
        if op['price'] < 0.01:
            op['price'] = 'negligible price'
        else:
            op['price'] = round(op['price'],2)
    return render_template('questionMarket.html',user=current_user,question=list(map(changeTZ,question))[0],options=options)
# FIX ME the question[0] is because the html is designed to accept list and iterate but here there is only one list item and without [0] it can't show the question

@main.route('/processQuestion',methods=['POST'])
@login_required
def processQuestion():
    if request.method == 'POST':
        req = request.get_json(force=True)
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))
        req['transaction_id'] = transaction_id
        producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send('transactions-stream-input-reborn', req)
        ret = register_kafka_listener(req['transaction_id'])
        if ret:
            url = '/portfolio'
        else:
            url = '/questionMarket'
        return url

@main.route('/estimate',methods=['POST'])
@login_required
def estimate():
    questionIdx = session['questionIdx']
    question = getTableByQuestionIdx('Questions', questionIdx)
    options = getTableByQuestionIdx('Options', questionIdx)
    options = row_to_dict(options)
    before_cost = calc_cost(options,None)
    if request.method == 'POST':
        req = request.get_json(force=True)
        after_cost = calc_cost(options,req)
        cost_of_trade = {'cost':abs(COST_SCALING_FACTOR*(after_cost-before_cost)),'isBuy':req['isBuy']}
    return jsonify(payload=cost_of_trade,code=200)

@main.route('/portfolio',methods=['GET','POST'])
@login_required
def portfolio():
    user_id = current_user.user_id
    portfolio = getPortfolioByUserIdx(user_id)
    purchase = {}
    for i in range(len(portfolio)):
       option = getOptionByOptionId(portfolio[i]['option_id'])[0]
       question = getTableByQuestionIdx('Questions',option['question_id'])[0]
       purchase[i+1] = {'question_text':question['question_text'],'option_text':option['option_text'],'num_shares':portfolio[i]['num_shares']}
    return render_template('portfolio.html',purchase=purchase)

@main.route('/legal')
def legal():
    return render_template('legal.html')
