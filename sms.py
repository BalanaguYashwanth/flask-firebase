import os
from flask import Flask, request, jsonify
#from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
import pyrebase
from flask_cors import CORS
import io
import json
from twilio.twiml.messaging_response import MessagingResponse
import requests 
import json
from twilio.rest import Client

#auth = firebase.auth()
#from firebase_admin import auth

app=Flask(__name__)
#cred = credentials.Certificate("key.json")
#default_app=firebase_admin.initialize_app(cred)
CORS(app)
#db = firestore.client()
#todo_ref=db.collection('todos')
#pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))

@app.route("/")
def home():
    return "hello all"

@app.route("/sms",methods=['POST'])
def sms_reply():
    msg1=request.data
    msg1=msg1.decode('utf-8')
    newmsg=msg1.split()
    print(newmsg[0])
    data={'text':newmsg[0],'phone_number':newmsg[1]}
    response=requests.post(url="http://cloud.smsindiahub.in/vendorsms/pushsms.aspx?user=yamahaconnex&password=Yamaha@12345&msisdn="+newmsg[1]+"&sid=SIHIND&msg=Dear%20customer,%20Your%20LPG%20has%20been%20booked%20Reference%20ID%207896541255.&fl=0&gwid=2")
    #print(response,response.text)
    return 'ok'

if __name__=="__main__":
    app.run(debug=True)
