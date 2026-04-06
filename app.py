import os
import requests
import json
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# --- بياناتك الثابتة ---
FB_TOKEN = "EAARkORIGoHIBRC4RXZC29byL6kwhyyfiZB4ofvCrjWosD0c59chS9EpIQoSSqtUeEpL2BpZAZAoMXBsoFZBTXFkawQFDRhfTP57vCyVCQbzSTLNE6a2TwLFeSaxMbicpzw0fZByucFvtzITuTDAKTgIs5EeR45tlfRKCMIC6fKva9QYq9WBwISvNBqfZAmvylLzkgZDZD"
PHONE_NUMBER_ID = "1081197188408116"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GEMINI_KEY = "AIzaSyAio9JpXStGfiLtqRWJfaFOFvq6aHgSjZo"

# إعداد Gemini بطريقة متوافقة تماماً
genai.configure(api_key=GEMINI_KEY)
# استخدمنا 'gemini-1.5-flash' بدون بادئة 'models/' لأن المكتبة تضيفها تلقائياً في النسخ الجديدة
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json()
    try:
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            msg_body = data['entry'][0]['changes'][0]['value']['messages'][0]
            user_msg = msg_body['text']['body']
            user_phone = msg_body['from']

            # طلب الرد من ذكاء Gemini
            response = model.generate_content(user_msg)
            ai_reply = response.text

            # إرسال الرد لواتساب
            send_whatsapp(user_phone, ai_reply)
    except Exception as e:
        print(f"حدث خطأ أثناء المعالجة: {e}")
    return "OK", 200

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
