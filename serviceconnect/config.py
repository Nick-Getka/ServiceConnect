import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'practice1234'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://'+\
                os.environ.get("POSTGRES_USER")+':'+\
                os.environ.get("POSTGRES_PASSWORD")+'@'+\
                os.environ.get("POSTGRES_HOST")+\
                ':5432/'+os.environ.get("POSTGRES_DB")


class ProductionConfig(Config):
    DEBUG = False
    SID = os.environ.get("TWILIO_SID")
    AUTH = os.environ.get("TWILIO_AUTH")
    FROM = os.environ.get("TWILIO_NUM")

class TestingConfig(Config):
    DEBUG = True
    SID = os.environ.get("TWILIO_SID_TEST")
    AUTH = os.environ.get("TWILIO_AUTH_TEST")
    FROM = os.environ.get("TWILIO_NUM_TEST")
