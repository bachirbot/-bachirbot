منimport os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

VERIFY_TOKEN = "bachir123"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
                        # استخدام الطريقة المباشرة لتوليد المحتوى
                        model = genai.GenerativeModel('gemini-pro')
                        response = model.generate_content(message_text)
                        if response and response.text:
                            reply_text = response.text
                    except Exception as e:
                        print(f"Gemini API Error: {e}")
                        # إذا حدث خطأ، نضع رسالة توضح الخطأ لنتأكد منه
                        reply_text = f"مرحباً يا بشير، استلمت رسالتك ولكن مفتاح Gemini API يحتاج للتحقق. الخطأ: {str(e)}"

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

