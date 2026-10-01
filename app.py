import os
import logging
import requests
from flask import Flask, request
import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "MY_SECURE_VERIFY_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

GRAPH_API_VERSION = "v19.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def get_user_first_name(sender_id: str) -> str:
    url = f"{FACEBOOK_GRAPH_URL}/{sender_id}"
    params = {
        "fields": "first_name",
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("first_name", "صديقي")
    except Exception as e:
        logger.error(f"Error fetching user name: {e}")
        return "صديقي"


def generate_gemini_reply(first_name: str, user_message: str) -> str:
    if not GEMINI_API_KEY:
        return f"أهلاً {first_name}، مفتاح الذكاء الاصطناعي غير معرّف."

    prompt = (
        f"أنت مساعد افتراضي ذكي لصفحة فيسبوك. اسم المستخدم الذي يراسلك هو '{first_name}'. "
        f"خاطبه باسمه بشكل لطيف، وأجب عن سؤاله التالي بدقة ومباشرة باللغة العربية الفصحى:\n\n"
        f"السؤال: {user_message}"
    )

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")

    return f"أهلاً {first_name}، تلقيت رسالتك، تفضل بطرح سؤالك."


def send_messenger_message(recipient_id: str, message_text: str):
    url = f"{FACEBOOK_GRAPH_URL}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}

    if len(message_text) > 2000:
        message_text = message_text[:1996] + "..."

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }

    try:
        requests.post(url, params=params, headers=headers, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    data = request.get_json()
    if not data or data.get("object") != "page":
        return "EVENT_RECEIVED", 404

    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")
            message = messaging_event.get("message")

            if message and "text" in message and not message.get("is_echo"):
                user_text = message["text"]
                first_name = get_user_first_name(sender_id)
                ai_reply = generate_gemini_reply(first_name, user_text)
                send_messenger_message(sender_id, ai_reply)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
