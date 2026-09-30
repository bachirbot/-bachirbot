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
    return "Bot is running and connected!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Error", 403
    
    try:
        d = request.json
        messaging_event = d['entry'][0]['messaging'][0]
        
        # التأكد من أن الرسالة تحتوي على نص مرسل من المستخدم
        if 'message' in messaging_event and 'text' in messaging_event['message']:
            s = messaging_event['sender']['id']
            t = messaging_event['message']['text'].strip()
            
            reply_text = "أهلاً بك يا بشير. جاري معالجة طلبك..."
            
            # محاولة جلب الإجابة من الذكاء الاصطناعي
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=t,
                )
                if response and response.text:
                    reply_text = response.text
            except Exception as ai_error:
                print("AI Error Details:", ai_error)
                reply_text = f"أهلاً بك يا بشير. لقد استلمت سؤالك: '{t}' وأنا أجهزه لك الآن!"

            # إرسال الرد عبر فيسبوك ماسنجر
            url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
            payload = {
                "recipient": {"id": s},
                "message": {"text": reply_text}
            }
            res = requests.post(url, json=payload)
            print("Facebook API Response:", res.text)
            
    except Exception as e:
        print("Webhook Main Error:", e)
        
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
