# apps.members.models
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#User table used to store user data including phone, zip and reminder settings
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    phone_num = db.Column(db.String(10), nullable=False)
    zip_code = db.Column(db.String(5), nullable=False)
    reminder = db.Column(db.Boolean)


    def __init__(self, phone_num, zip_code, reminder):
        self.phone_num = phone_num
        self.zip_code = zip_code
        self.reminder = reminder
