from flask import Blueprint, render_template, request, session, redirect
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
#               print('here')
               op['num_of_outstanding_shares'] += int(kafka_dict['numShares'])
   num_outstanding = np.array([op['num_of_outstanding_shares'] for op in options])
   cost = B*np.log(np.sum(np.exp(num_outstanding/B)))
   return cost

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
    if request.method == 'POST':
        req = request.form.to_dict()
        session['questionIdx'] = req['qId']
        return redirect('/questionMarket')
    return render_template('profile.html', user=current_user, questions=list(map(changeTZ,  active_questions)))
    #return render_template('profile.html', name=current_user.fb_user_id,credits=current_user.credits)

# https://stackoverflow.com/questions/53263393/is-there-a-python-api-for-event-driven-kafka-consumer/53267676#53267676
def register_kafka_listener(transaction_id):
    # Poll kafka
    # def poll():
        # Initialize consumer Instance
    # print("Entered kafka listener for t_id = {}".format(transaction_id))
    # consumer = KafkaConsumer('transactions-out',auto_offset_reset='earliest', bootstrap_servers=['localhost:9092'])
    consumer = KafkaConsumer('transactions-out',bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest')
    # print("About to start polling for topic:", topic)
    # print("Started Polling for topic:", topic)
    # consumer.poll(timeout_ms=6000)
    # print("opened consumer, before loop1")
    for msg in consumer:
        # print("Entered the loop\nKey: ",msg.key," Value:", msg.value)
        y = json.loads(msg.value)
        if y['transaction_id'] == transaction_id:
            return y['status']
        # listener(msg, transaction_id)
    # print("About to register listener to topic:", topic)
    # t1 = threading.Thread(target=poll)
    # t1.start()
    # print("started a background thread")
    return False
#def kafka_listener(data, t_id):
#    print("Image Ratings:\n", data.value.decode("utf-8")

def row_to_dict(row):
    dict = [{column: value for column, value in rowproxy.items()} for rowproxy in row]
    return dict

@main.route('/questionMarket',methods=['GET','POST'])
@login_required
def questionMarket():
    questionIdx = session['questionIdx']
    question = getTableByQuestionIdx('Questions', questionIdx)
    options = getTableByQuestionIdx('Options', questionIdx)
    # options = [{column: value for column, value in rowproxy.items()} for rowproxy in options]
    options = row_to_dict(options)

    before_cost = calc_cost(options,None)

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
                kafkaDict['transaction_id']=''.join(random.choices(string.ascii_uppercase + string.digits, k=100))
                after_cost = calc_cost(options,kafkaDict)
                cost_of_trade = COST_SCALING_FACTOR*(after_cost-before_cost)
                producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))
                producer.send('transactions-stream-input-reborn', kafkaDict)
                ret = register_kafka_listener(kafkaDict['transaction_id'])
                print("return value from listener ", ret)
                if ret:
                    return redirect('/portfolio')
                else:
                    return redirect('/questionMarket')
    return render_template('questionMarket.html',user=current_user,question=list(map(changeTZ,question))[0],options=options)
# FIX ME the question[0] is because the html is designed to accept list and iterate but here there is only one list item and without [0] it can't show the question



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
#    for p in purchase:
       # print('{}: {}'.format(p,purchase[p]))
    return render_template('portfolio.html',purchase=purchase)

@main.route('/legal')
def legal():
    return render_template('legal.html')
