import serviceconnect.config
from serviceconnect.models import db
import os
import threading
import schedule
import time
import logging
import multiprocessing
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from flask import Flask
from twilio.rest import Client

#Instantiating Flask
app = Flask(__name__)



# This level filter was taken from https://stackoverflow.com/questions/8162419/python-logging-specific-level-only
# This was intended to solve the exact problem I am working on and I wished to avoid accidental plagarism by citing it here
class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.__level = level
    def filter(self, logRecord):
        return logRecord.levelno == self.__level



class ReminderProcess(multiprocessing.Process):
    def __init__(self, ):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
    def run(self):
        try :
            while not self.exit.is_set():
                schedule.every().sunday.at("12:00").do(self._send_reminder)
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Reminder Process stopping due to KeyboardInterrupt")
            self.stop_process()
    def stop_process(self):
        self.exit.set()

    #Scheduled Reminders  - Use Case 3
    def _send_reminder(self):
        """Sends the users the appropriate reminders via sms"""
        with app.app_context():
            for user in db.session.query(User).filter_by(active=True):
                if user.reminder:
                    mess = "Thank you for using textFood! Remember you can \
                        text us anytime for information on helpful services nearby! \
                        \n You can text food for infomation on emergency \
                            food, food pantries, and free meals \
                        \n You can text legal for infomation on legal aid \
                            and Government Programs \
                        \n You can text medical for infomation on mental \
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



def prep_app(environment) :
    #Configuring the Flask App
    conf=config.TestingConfig
    if environment == 'PRODUCTION':
        conf = config.ProductionConfig
        #Start Scheduled Reminders Thread only in production
        t = ReminderProcess()
        try :
            t.start()
        except:
            t.stop_process()
    app.config.from_object(conf)

    #Setting up Twilio Client
    client = Client(conf.SID, conf.AUTH)

    #Instantiating the SQL DB
    db.init_app(app)
    with app.app_context():
        db.create_all()

    #Configuring Logger
    app.logger.setLevel(logging.INFO)
    #Store the user data
    data_format = logging.Formatter('%(asctime)s: %(message)s')
    data_handler = TimedRotatingFileHandler('/home/ngetka/Desktop/ServiceConnect/log/data.log',when='W6',backupCount=100)
    data_handler.setLevel(logging.INFO)
    data_handler.setFormatter(data_format)
    data_handler.addFilter(LevelFilter(logging.INFO))
    app.logger.addHandler(data_handler)
    #Store error data for debugging
    error_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_handler = RotatingFileHandler('/home/ngetka/Desktop/ServiceConnect/log/error.log', maxBytes=100000, backupCount=5)
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(error_format)
    app.logger.addHandler(error_handler)

    #Importing Routes
    from . import views
    return app
