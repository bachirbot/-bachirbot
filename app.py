import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "bachir123"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

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
        t = d['entry'][0]['messaging'][0]['message']['text'].strip()
        
        # تحديد الرد الذكي بناءً على ما كتبته
        if "سلام" in t or "مرحباً" in t or "كيف حالك" in t:
            reply_text = "أهلاً بك يا بشير! أنا بصحة ممتازة وجاهز لمساعدتك في أعمالك. كيف يمكنني خدمتك اليوم؟"
        elif "من أنت" in t:
            reply_text = "أنا Bachirbot، مساعدك الشخصي الرقمي."
        else:
            reply_text = f"لقد استلمت رسالتك: '{t}'. أنا أعمل بكامل كفاءتي لتنفيذ أوامرك القادمة!"

        # إرسال الرد الذكي عبر الماسنجر
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        requests.post(url, json={"recipient": {"id": s}, "message": {"text": reply_text}})
    except:
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
