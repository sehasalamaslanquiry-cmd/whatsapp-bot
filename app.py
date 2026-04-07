import os
import requests
import json
from flask import Flask, request

app = Flask(__name__)

# --- بياناتك ---
FB_TOKEN = "EAARkORIGoHIBRCd4f4AlYR9vHrQinu97fMjyD8ZAayYHjQbQtEwCGev2FHJRHJs21yJyaEAo88ezX2nzoiZBSy8L6iAdETr0OuqaVexx6AhQY4yvpLXCmlOjmkOJu37FhaH1gxIE0DOKzNWrq7nPuc7OQryaAv6KWRB15H9umR03PmCh3QlvjMvyNvQuWwU0QRjFUs5gQqboOlXsxr0ZAJfZAZCyvJ2aLKODFVm1ZADN5QwS7pxs8gzwZDZD"
PHONE_NUMBER_ID = "1081197188408116"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GEMINI_KEY = "AIzaSyAio9JpXStGfiLtqRWJfaFOFvq6aHgSjZo"

def get_gemini_response(user_text):
    # مخاطبة Gemini مباشرة عبر الرابط بدون مكتبات وسيطة
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": user_text}]}]}
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # استخراج النص من الرد
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "عذراً، واجهت مشكلة في فهم الرسالة."

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
            msg_obj = data['entry'][0]['changes'][0]['value']['messages'][0]
            user_msg = msg_obj['text']['body']
            user_phone = msg_obj['from']

            # الحصول على الرد من الدالة الجديدة
            ai_reply = get_gemini_response(user_msg)
            
            # إرسال الرد لواتساب
            send_whatsapp(user_phone, ai_reply)
    except Exception as e:
        print(f"Error: {e}")
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
