from flask_sqlalchemy import SQLAlchemy
from models import User

class ServiceConnect(object):
    def __init__(self, db, from_num, query, cookies) :
        self.db = db
        self.from_num = from_num
        self.query = query
        self.cookies = cookies
