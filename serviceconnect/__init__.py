import serviceconnect.config
from serviceconnect.models import db
import os
import threading
import schedule
import time
import logging
from flask import Flask
from threading import Thread
from twilio.rest import Client
from logging.handlers import RotatingFileHandler




#Instantiating Flask
app = Flask(__name__)

#Scheduled Reminders  - Use Case 3
def send_reminder():
    """Sends the users the appropriate reminders via sms"""
    with app.app_context():
        for user in db.session.query(User).filter_by(active=True):
            mess = "Thank you for using textFood! Remember you can text us any \
                    time for information on helpful services nearby!"
            if user.reminder:
                if user.food_reminder:
                    mess += "\n You can text food for infomation on emergency \
                                food, food pantries, and free meals"
                if user.legal_reminder:
                    mess += "\n You can text legal for infomation on legal aid \
                                and Government Programs"
                if user.medical_reminder:
                    mess += "\n You can text medical for infomation on mental \
                                health and primary care"
                client.messages.create(
                    to = "+1"+user.phone_num,
                    from_ = os.environ.get('TWILIO_NUM'),
                    body = mess
                )
                user.food_reminder = True
                user.legal_reminder = True
                user.medical_reminder = True
                db.session.commit()
def schedule_start():
    while True:
        schedule.run_pending()
        time.sleep(1)

def prep_app(environment) :
    #Configuring the Flask App
    conf=config.TestingConfig
    if environment == 'PRODUCTION':
        conf = config.ProductionConfig
        #Start Scheduled Reminders Thread only in production
        schedule.every().sunday.at("12:00").do(send_reminder)
        t = Thread(target=schedule_start)
        t.start()
    app.config.from_object(conf)

    #Setting up Twilio Client
    client = Client(conf.SID, conf.AUTH)

    #Instantiating the SQL DB
    db.init_app(app)
    with app.app_context():
        db.create_all()

    #Importing Routes
    from . import views
    return app
