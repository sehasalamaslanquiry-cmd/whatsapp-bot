import os
import requests
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- بياناتك الثابتة ---
FB_TOKEN = "EAARkORIGoHIBRC4RXZC29byL6kwhyyfiZB4ofvCrjWosD0c59chS9EpIQoSSqtUeEpL2BpZAZAoMXBsoFZBTXFkawQFDRhfTP57vCyVCQbzSTLNE6a2TwLFeSaxMbicpzw0fZByucFvtzITuTDAKTgIs5EeR45tlfRKCMIC6fKva9QYq9WBwISvNBqfZAmvylLzkgZDZD"
PHONE_NUMBER_ID = "1081197188408116"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GEMINI_KEY = "AIzaSyAio9JpXStGfiLtqRWJfaFOFvq6aHgSjZo"

# إعداد Gemini
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
    print(f"Received Data: {data}") # سطر لمراقبة الرسائل الواصلة في الـ Logs
    try:
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message_obj = data['entry'][0]['changes'][0]['value']['messages'][0]
            user_msg = message_obj['text']['body']
            user_phone = message_obj['from']

            # توليد الرد من Gemini
            response = model.generate_content(user_msg)
            ai_reply = response.text

            # إرسال الرد
            send_whatsapp(user_phone, ai_reply)
    except Exception as e:
        print(f"Error: {e}") # سطر لمعرفة سبب الفشل إن حدث
    return "OK", 200

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {FB_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    # تعديل مهم: استخدام json=payload لضمان إرسال البيانات بشكل صحيح
    response = requests.post(url, headers=headers, json=payload)
    print(f"WhatsApp Response: {response.json()}") # سطر لمراقبة رد فيسبوك

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
