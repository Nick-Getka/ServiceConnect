from serviceconnect.models import db
from flask import Flask
from threading import Thread
from twilio.rest import Client
import serviceconnect.config
import os
import threading
import schedule
import time

#Instantiating Config File
conf=config.DevelopmentConfig
if os.environ['ENV']=='production':
    conf = config.ProductionConfig

#Instantiating Flask
app = Flask(__name__)

#Setting up Twilio Client
client = Client(conf.SID, conf.AUTH)

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

def prep_app(pdb = db) :
    schedule.every().sunday.at("12:00").do(send_reminder)
    t = Thread(target=schedule_start)
    t.start()
    app.config.from_object(conf)
    pdb.init_app(app)
    with app.app_context():
        pdb.create_all()

    from . import views
    return app
