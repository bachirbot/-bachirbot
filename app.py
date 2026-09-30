import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

VERIFY_TOKEN = "bachir123"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/")
def home():
    return "Bachirbot AI is online!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Error", 403
    
    try:
        data = request.json
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text'].strip()
                    
                    print(f"Message received: {message_text}")
                    
                    reply_text = "أهلاً بك يا بشير. جاري معالجة طلبك..."
                    
                    try:
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=message_text,
                        )
                        if response and response.text:
                            reply_text = response.text
                    except Exception as e:
                        print(f"GenAI Error Details: {e}")
                        reply_text = f"عذراً يا بشير، حدث خطأ في مفتاح الـ API أو الاتصال. الخطأ هو: {str(e)}"

                    # إرسال الإجابة عبر ماسنجر
                    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                    payload = {
                        "recipient": {"id": sender_id},
                        "message": {"text": reply_text}
                    }
                    res = requests.post(url, json=payload)
                    print("FB Response:", res.text)
                    
    except Exception as err:
        print(f"Webhook Error: {err}")
        
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
