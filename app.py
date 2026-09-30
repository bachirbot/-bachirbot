import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

VERIFY_TOKEN = "bachir123"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# إعداد مفتاح جيميناي بالطريقة المستقرة
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.route("/")
def home():
    return "Bachirbot is running stably!"

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
                    
                    print(f"Received message: {message_text}")
                    
                    reply_text = "أهلاً بك يا بشير. جاري توليد الإجابة..."
                    
                    try:
                        # استخدام النموذج المعتمد والمستقر
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(message_text)
                        if response and response.text:
                            reply_text = response.text
                    except Exception as ai_err:
                        print(f"AI Error: {ai_err}")
                        reply_text = f"أهلاً يا بشير، لقد تلقيت رسالتك: '{message_text}' وأنا هنا لمساعدتك."

                    # إرسال الرد عبر الماسنجر
                    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                    payload = {
                        "recipient": {"id": sender_id},
                        "message": {"text": reply_text}
                    }
                    res = requests.post(url, json=payload)
                    print(f"FB Response status: {res.status_code}")
                    
    except Exception as err:
        print(f"Webhook Error: {err}")
        
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
