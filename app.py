
import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- ضع بياناتك هنا ---
FB_TOKEN = "EAARkORIGoHIBRC4RXZC29byL6kwhyyfiZB4ofvCrjWosD0c59chS9EpIQoSSqtUeEpL2BpZAZAoMXBsoFZBTXFkawQFDRhfTP57vCyVCQbzSTLNE6a2TwLFeSaxMbicpzw0fZByucFvtzITuTDAKTgIs5EeR45tlfRKCMIC6fKva9QYq9WBwISvNBqfZAmvylLzkgZDZD"
PHONE_NUMBER_ID = "1081197188408116"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GEMINI_KEY = "AIzaSyAio9JpXStGfiLtqRWJfaFOFvq6aHgSjZo"

# إعداد ذكاء Gemini
genai.configure(api_key=GEMINI_KEY)
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
        # استخراج الرسالة ورقم المرسل
        message_obj = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_msg = message_obj['text']['body']
        user_phone = message_obj['from']

        # 1. إرسال النص لـ Gemini ليصيغ الرد
        response = model.generate_content(user_msg)
        ai_reply = response.text

        # 2. إرسال رد الذكاء الاصطناعي لواتساب
        send_whatsapp(user_phone, ai_reply)
    except:
        pass
    return "OK", 200

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    json_data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=json_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
