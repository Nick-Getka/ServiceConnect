import os
from flask import Flask, request, redirect
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse, Message
app = Flask(__name__)
SID = os.environ.get("TWILIO_SID_TEST")
AUTH = os.environ.get("TWILIO_AUTH_TEST")
FROM = os.environ.get("TWILIO_NUM_TEST")




@app.route('/sms', methods=['post'])
def sms():
    return "Hello"



if __name__ == '__main__':
    dev = True
    if os.environ.get('ENV') is not None :
        if os.environ.get('ENV') =='production' :
            dev = False
            SID = os.environ.get('TWILIO_SID')
            AUTH = os.environ.get('TWILIO_AUTH')
            FROM = os.environ.get("TWILIO_NUM")

    client = Client(SID, AUTH)

    client.api.account.messages.create(
        to="+13013009966",
        from_=FROM,
        body="test")
    app.run(debug=dev, host='0.0.0.0')
