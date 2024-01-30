from flask import Flask, request, jsonify
import requests
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv('.env')

@app.route("/")
def home():
    return "Main"

@app.route("/helloWorld", methods=["GET"])
def helloWorld():
    return "Hello World"

@app.route("/webhook", methods=["GET"])
def webhookGET():
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print('WEBHOOK VERIFICADO')
        return challenge, 200
    else:
        return 'ERROR', 403

@app.route("/webhook", methods=["POST"])
def webhookPOST():
    data = request.data
    body = json.loads(data.decode('utf-8'))

    if 'object' in body and body['object'] == 'page':
        entries = body['entry']
        for entry in entries:
            webhookEvent = entry['messaging'][0]
            print(webhookEvent)

            senderPsid = webhookEvent['sender']['id']
            print('Sender PSID: {}',format(senderPsid))

            if 'message' in webhookEvent:
                handleMessage(senderPsid, webhookEvent['message'])
                return 'EVENT_RECEIVED', 200
    else:
        return 'ERROR', 400

def handleMessage(senderPsid, receivedMessage):
    if 'text' in receivedMessage:
        response = {
            "text": 'You just send me {}'.format(receivedMessage['text'])
        }
        callSendAPI(senderPsid,response)
    else:
        response = {
            "text": 'This chatbot only accepts text messages'
        }
        callSendAPI(senderPsid,response)

def callSendAPI(senderPsid,response):
    resquestBody = {
        'recipient': 
        {
            'id': senderPsid
        },
        'message': response,
        'messaging_type':'RESPONSE'
    }
    headers = {
        'content-type': 'application/json'
    }
    url = 'https://graph.facebook.com/v18.0/me/messages?access_token={}'.format(os.getenv('PAGE_ACCESS_TOKEN'))
    r = requests.post(url, json=resquestBody, headers=headers)
    print(r.text)


if __name__ == "__main__":
    app.run(debug=True)
# http://127.0.0.1:5000/webhook?hub.verify_token=stringUnicoParaTuAplicacion&hub.challenge=CHALLENGE_ACCEPTED&hub.mode=subscribe