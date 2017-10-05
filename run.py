import os
import threading
import config
import re
import random
import xml.etree.ElementTree as et
from models import User
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse, Message



#Instantiating Flask
app = Flask(__name__)
conf=config.DevelopmentConfig
if os.environ['ENV']=='production':
    conf = config.ProductionConfig
app.config.from_object(conf)

#Setting up the DB
from models import db

#Setting up Twilio Client
client = Client(conf.SID, conf.AUTH)

#Parsing Decision Tree
typology = et.parse('typology.xml')



def _isRegistered(from_num) :
    return db.session.query(User.phone_num).filter_by(phone_num=from_num)\
                .scalar() is not None

def _register(from_num, zip_code):
    valid_zip = [20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008, 20009, \
                 20010, 20011, 20012, 20015, 20016, 20017, 20018, 20019, 20020, \
                 20024, 20032, 20036, 20037, 20045, 20052, 20053, 20057, 20064, \
                 20202, 20204, 20228, 20230, 20240, 20245, 20260, 20307, 20317, \
                 20319, 20373, 20390, 20405, 20418, 20427, 20506, 20510, 20520, \
                 20535, 20540, 20551, 20553, 20560, 20565, 20566, 20593]
    zipc = re.findall(r'(\b\d{5}\b)', zip_code)
    ret = { 'message': "Standin", 'cookies': None }
    if len(zipc) == 0 :
        ret['message'] = "Invalid Zip Code, please try again!"
        ret['cookies'] = {'lastText': 'notRegistered'}
    elif len(zipc) > 1 :
        ret['message'] = "Please enter one 5 digit zipcode"
        ret['cookies'] = {'lastText': 'notRegistered'}
    elif int(zipc[0]) not in valid_zip :
        ret['message'] = "The textFood is only available in DC."
        ret['cookies'] = None
    else :
        getReminders = bool(random.getrandbits(1))
        db.session.add(User(from_num, zipc[0], getReminders))
        db.session.commit()
        ret['message'] = "{} at zip code {} is now registered to the textFood service".format(from_num, zipc[0])
    return ret

def _processInitialQuery(query):
    ret = {
            'message': "No Information found on {}".format(query),
            'cookies': None
            }

    root = typology.getroot()
    target = None
    for child in root :
        if child.get('name') == query:
            target = child

    if target is not None :
        sub = []
        for child in target :
            sub.append(child)
        ret['message'] = "Please text one of the following for information on the relevant sub category \n"
        for s in sub:
            ret['message'] += " {} - {} \n".format(s.get('name'), s.text)
        ret['cookies'] = {
            'lastText': "initialQuery",
            'initialQuery': query
        }
    return ret
def _processSubQuery(query, cookies):
    root = typology.getroot()
    ret = {
            'message': "No Information found on {}".format(query),
            'cookies': cookies
            }
    target = None
    for child in root :
        if child.get('name') == cookies.get('initialQuery'):
            for sub in child :
                if sub.get('name') == query:
                    target = sub
    if sub is not None :
        ret['message'] = "For more information on {} see {}".format(query, sub.find('data').text)
        ret['cookies'] = None
    return ret

def _cancel():
    return {
                'message': "Standin",
                'cookies': None
            }
def _comfirmCancel():
    return {
                'message': "Standin",
                'cookies': None
            }

def processText(from_num, query, cookies):
    query = query.lower()
    if query == "clear":
        return {'message': "Clearing", 'cookies': None}

    ret = {'message': "Default Message", 'cookies': None}
    if cookies is None :
        if _isRegistered(from_num) :
            ret = _processInitialQuery(query)
        else :
            ret = {
                'message': "Welcome to TextFood! To register and start using the TextFood service please text your home zip code",
                'cookies': { 'lastText': 'notRegistered' }
            }
    else :
        if cookies.get('lastText') == 'notRegistered':
            ret = _register(from_num, query)
        elif cookies.get('lastText') == 'initialQuery':
            ret = _processSubQuery(query, cookies)
        elif cookies.get('lastText') == 'cancel':
            ret = _comfirmCancel()
        else :
            ret = {'message': "ERROR", 'cookies': None}
    return ret




#Flask Routes
@app.route('/', methods=['POST'])
def sms():
    from_number = request.form['From'][2:]
    query = request.form['Body']
    cookies = session.get('cookies', None)

    ret = processText(from_number, query, cookies)
    session['cookies'] = ret.get('cookies')

    resp = MessagingResponse()
    respText = ret.get('message')
    resp.message(respText)
    return str(resp)


if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')
