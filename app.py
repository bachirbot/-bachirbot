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
    return "Bot is running with AI!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Error", 403
    try:
        d = request.json
        s = d['entry'][0]['messaging'][0]['sender']['id']
        t = d['entry'][0]['messaging'][0]['message']['text'].strip()
        
        # محاولة توليد الإجابة عبر الذكاء الاصطناعي
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=t,
            )
            reply_text = response.text
        except Exception as ai_err:
            # رد احتياطي فوري لو حدث أي تأخير في الاتصال
            reply_text = f"أهلاً بك يا بشير. لقد استلمت سؤالك: '{t}' وأنا أجهزه لك فوراً!"

        # إرسال الإجابة عبر الماسنجر
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        requests.post(url, json={"recipient": {"id": s}, "message": {"text": reply_text}})
    except Exception as e:
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
