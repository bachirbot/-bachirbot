import os
import logging
import requests
from flask import Flask, request, jsonify

# إعداد السجلات (Logging) لمتابعة العمليات وتتبع الأخطاء
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==========================================
# متغيرات البيئة والإعدادات (Environment Variables)
# ==========================================
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "MY_SECURE_VERIFY_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-flash-latest"
GRAPH_API_VERSION = "v19.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


# ==========================================
# الدوال المساعدة (Helper Functions)
# ==========================================

def get_user_first_name(sender_id: str) -> str:
    """
    جلب الاسم الأول الحقيقي للمستخدم من Facebook Graph API باستخدام sender_id.
    """
    url = f"{FACEBOOK_GRAPH_URL}/{sender_id}"
    params = {
        "fields": "first_name",
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        first_name = data.get("first_name")
        if first_name:
            logger.info(f"تم جلب الاسم بنجاح: {first_name} للمستخدم {sender_id}")
            return first_name
    except requests.exceptions.RequestException as e:
        logger.error(f"خطأ أثناء جلب اسم المستخدم من Graph API: {e}")

    # اسم احتياطي في حال تعذر الوصول لبيانات المستخدم أو تقييد الصلاحيات
    return "صديقي"


def generate_gemini_reply(first_name: str, user_message: str) -> str:
    """
    توليد إجابة ذكية ودقيقة باللغة العربية الفصحى عبر Gemini API
    مع توجيه النموذج لمخاطبة المستخدم باسمه وبإيجاز وموضوعية.
    """
    if not GEMINI_API_KEY:
        logger.error("لم يتم تعيين GEMINI_API_KEY")
        return f"مرحباً {first_name}، هناك مشكلة مؤقتة في خادم الذكاء الاصطناعي."

    system_instruction = (
        "أنت مساعد افتراضي ذكي ولبق لصفحة فيسبوك. "
        f"يجب عليك دائماً مخاطبة المستخدم باسمه الأول: '{first_name}'. "
        "أجب عن سؤاله باللغة العربية الفصحى فقط، بإجابة دقيقة، مباشرة، ومفيدة جداً، "
        "وبموضوعية تامة بدون حشو أو تكرار ممل أو مقدمات طويلة."
    )

    payload = {
        "system_instruction": {
            "parts": [
                {"text": system_instruction}
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_message}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 800
        }
    }

    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            params=params,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        # استخراج النص الناتج من استجابة جيمناي
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return reply_text
    except Exception as e:
        logger.error(f"خطأ أثناء توليد الرد من Gemini API: {e}")
        return f"أهلاً {first_name}، واجهت مشكلة في معالجة طلبك حالياً، يرجى المحاولة لاحقاً."


def send_messenger_message(recipient_id: str, message_text: str):
    """
    إرسال الرسالة إلى المستخدم عبر Facebook Messenger Send API.
    مع مراعاة الحد الأقصى لطول الرسالة في ماسنجر (2000 حرف).
    """
    url = f"{FACEBOOK_GRAPH_URL}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}

    # اقتطاع الرسالة إذا تجاوزت الحد المسموح به في ماسنجر لتفادي رفض فيسبوك للطلب
    if len(message_text) > 2000:
        message_text = message_text[:1996] + "..."

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }

    try:
        response = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"تم إرسال الرد بنجاح إلى المستخدم {recipient_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"فشل إرسال الرسالة عبر Send API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"تفاصيل الخطأ من فيسبوك: {e.response.text}")


# ==========================================
# مسارات الويب هوك (Webhook Endpoints)
# ==========================================

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    مسار التحقق المطلوب من قِبل فيسبوك عند ربط الويب هوك (GET).
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("تم التحقق من الويب هوك بنجاح بواسطة فيسبوك.")
        return challenge, 200
    else:
        logger.warning("فشل التحقق من الويب هوك: رمز التحقق غير متطابق.")
        return "Verification token mismatch", 403


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """
    مسار استقبال الرسائل والأحداث الواردة من ماسنجر (POST).
    """
    data = request.get_json()

    if not data or data.get("object") != "page":
        return "EVENT_RECEIVED", 404

    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")
            message = messaging_event.get("message")

            # التأكد من وجود رسالة نصية وأنها ليست صدى (echo) لرسائل البوت نفسه
            if message and "text" in message and not message.get("is_echo"):
                user_text = message["text"]
                logger.info(f"رسالة واردة من {sender_id}: {user_text}")

                # 1. جلب الاسم الأول الحقيقي للمستخدم
                first_name = get_user_first_name(sender_id)

                # 2. توليد الإجابة باستخدام Gemini
                ai_reply = generate_gemini_reply(first_name, user_text)

                # 3. إرسال الإجابة عبر Messenger Send API
                send_messenger_message(sender_id, ai_reply)

    # يجب الرد برمز 200 دائماً وبسرعة حتى لا يعيد فيسبوك إرسال الرسالة نفسها
    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    # تشغيل التطبيق على المنفذ 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
