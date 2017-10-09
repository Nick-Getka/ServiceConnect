import re
import random
import xml.etree.ElementTree as et
from .models import User
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse, Message
from . import app, db



#Parsing Decision Tree
typology = et.parse('serviceconnect/typology.xml')

#Flask Routes
@app.route('/', methods=['POST'])
def sms():
    from_num = request.form['From'][2:]
    initQuery = request.form['Body']
    query = cleanText(initQuery)
    cookies = session.get('cookies', None)

    ret = {'message': "Default Message", 'cookies': None}
    if cookies is not None:
        if cookies['lastText'] == 'notRegistered':
            ret = _register(from_num, query)
        elif cookies['lastText'] == 'cancel' :
            ret = _comfirmCancel(from_num, query)
    else :
        if _isRegistered(from_num) :
            ret = _processQuery(from_num, query, initQuery)
        else :
            ret = {
                'message': "Welcome to TextFood! To register and start using \
                            the TextFood service please text your home zip code",
                'cookies': { 'lastText': 'notRegistered' }
            }

    session['cookies'] = ret.get('cookies')
    resp = MessagingResponse()
    respText = ret.get('message')
    resp.message(respText)
    return str(resp)

#Misc Funtions
def cleanText(query):
    """cleanText cleans the original text of any non alphanumeric symbols and\
    coverts all to lower case"""
    query = query.lower()
    query = re.sub(r'[^0-9a-zA-Z]+', ' ', query)
    return query

#Registration - Use Case 1
def _isRegistered(from_num) :
    """isRegistered Tests to see if the number has been previously registered \
    to the ServiceConnect service by testing to see if the number exists in \
    the database"""
    return db.session.query(User.phone_num).filter_by(phone_num=from_num)\
                .scalar() is not None

def _register(from_num, zip_code):
    """_register registers a user to the service by creating a new record in \
    the database using the user's phone number and zip code.  It also validates \
    the zip code and sets the reminder settings for the user"""
    ret = { 'message': "Standin", 'cookies': None }
    valid_zip = [20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008, 20009, \
                 20010, 20011, 20012, 20015, 20016, 20017, 20018, 20019, 20020, \
                 20024, 20032, 20036, 20037, 20045, 20052, 20053, 20057, 20064, \
                 20202, 20204, 20228, 20230, 20240, 20245, 20260, 20307, 20317, \
                 20319, 20373, 20390, 20405, 20418, 20427, 20506, 20510, 20520, \
                 20535, 20540, 20551, 20553, 20560, 20565, 20566, 20593]
    zipc = re.findall(r'(\b\d{5}\b)', zip_code)
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
        ret['message'] = "{} at zip code {} is now registered to the textFood service"\
                         .format(from_num, zipc[0])
    return ret

#Direct Querying  - Use Case 2
def _processQuery(from_num, query, original):
    """_processQuery takes the users query text and returns the appropriate \
    information for the requested service."""
    #Default Response
    ret = {
            'message': "No information found on {}".format(original),
            'cookies': None
            }

    if re.match(r'stopt', query):
        ret = {
                'message': "To comfirm cancellation please input your home zip code",
                'cookies': {'lastText':'cancel'}
                }
    else:
        #Searching for requested xml element
        root = typology.getroot()
        parent = root
        target = None
        for child in root.iter() :
            if child.tag == 'category':
                parent = child
            if child.get('name') == query:
                target = child
                break
        #Composing text messessage based on requested element
        if target is not None :
            if target.tag == 'category':
                ret['message'] = "Please text one of the following for information on the relevant sub category \n"
                for sub in target.findall('service'):
                    ret['message'] += " {} - {} \n"\
                                        .format(sub.get('name'), sub.text)
            elif target.tag == 'service':
                user = db.session.query(User).filter_by(phone_num=from_num)\
                         .scalar()
                zipc = user.zip_code
                if user.reminder :
                    if parent.get('name') == 'food':
                        user.food_reminder = False
                    elif parent.get('name') == 'legal':
                        user.legal_reminder = False
                    elif parent.get('name') == 'medical':
                        user.medical_reminder = False
                db.session.commit()
                ret['message'] = "For more information on {} at zip code {} see {}"\
                                 .format(query, zipc, target.find("data").text)
    return ret

#Cancellation - Use Case 4
def _comfirmCancel(from_num, query):
    """_comfirmCancel deletes the user from the database after validating the \
    the users zip code"""
    user = db.session.query(User).filter_by(phone_num=from_num).scalar()
    if str(user.zip_code) == query :
        db.session.delete(user)
        ret = {
                    'message': "Your text food account has been cancelled",
                    'cookies': None
                }
    else :
        ret = {
                    'message': "Incorrect zip code your account has not been \
                                cancelled",
                    'cookies': None
                }
    db.session.commit()
    return ret
