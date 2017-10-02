import os
import threading
import config
from flask import Flask, request, redirect
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
db = SQLAlchemy(app)
#User table used to store user data including phone, zip and reminder settings
class Users(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    phone_num = db.Column(db.String(10), nullable=False)
    zip_code = db.Column(db.String(5), nullable=False)
    active = db.Column(db.Boolean)
    reminder = db.Column(db.Boolean)
    food_reminder = db.Column(db.Boolean)
    legal_reminder = db.Column(db.Boolean)
    money_reminder = db.Column(db.Boolean)

    def __init__(self, phone_num, zip_code, reminder):
        self.phone_num = phone_num
        self.zip_code = zip_code
        self.active = True
        self.reminder = reminder
        self.food_reminder = True
        self.legal_reminder = True
        self.money_reminder = True
db.create_all()

#Setting up Twilio Client
client = Client(conf.SID, conf.AUTH)


#Flask Routes
@app.route('/sms', methods=['post'])
def sms():
    return "Hello"



if __name__ == '__main__':
    app.run(host='0.0.0.0')
