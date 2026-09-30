import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "bachir123"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/")
def home():
    return "Bachirbot is running perfectly!"

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
                    
                    reply_text = "أهلاً يا بشير، جاري توليد الرد..."
                    
                    try:
                        # الاتصال المباشر بخدمة Gemini عبر HTTP API دون الحاجة لمكتبات معقدة
                        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                        headers = {"Content-Type": "application/json"}
                        payload_gemini = {
                            "contents": [{
                                "parts": [{"text": message_text}]
                            }]
                        }
                        
                        res = requests.post(gemini_url, json=payload_gemini, headers=headers)
                        if res.status_code == 200:
                            res_data = res.json()
                            reply_text = res_data['candidates'][0]['content']['parts'][0]['text']
                        else:
                            reply_text = f"عذراً يا بشير، رمز الاستجابة من جيميناي هو: {res.status_code}"
                    except Exception as e:
                        print(f"API Error: {e}")
                        reply_text = f"حدث خطأ أثناء الاتصال: {str(e)}"

                    # إرسال الرد عبر الماسنجر
                    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                    payload = {
                        "recipient": {"id": sender_id},
                        "message": {"text": reply_text}
                    }
                    requests.post(url, json=payload)
                    
    except Exception as err:
        print(f"Webhook Error: {err}")
        
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
