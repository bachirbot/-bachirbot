import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "bachir123"
PAGE_ACCESS_TOKEN = import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "bachir123"
PAGE_ACCESS_TOKEN = "EAAXQ..."

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Error", 403
    try:
        d = request.json
        s = d['entry'][0]['messaging'][0]['sender']['id']
        t = d['entry'][0]['messaging'][0]['message']['text']
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        requests.post(url, json={"recipient": {"id": s}, "message": {"text": f"أهلاً: {t}"}})
    except:
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Error", 403
    try:
        d = request.json
        s = d['entry'][0]['messaging'][0]['sender']['id']
        t = d['entry'][0]['messaging'][0]['message']['text']
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        requests.post(url, json={"recipient": {"id": s}, "message": {"text": f"أهلاً: {t}"}})
    except:
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
