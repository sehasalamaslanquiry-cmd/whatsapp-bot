import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- بياناتك المحدثة ---
FB_TOKEN = "EAARkORIGoHIBRC4RXZC29byL6kwhyyfiZB4ofvCrjWosD0c59chS9EpIQoSSqtUeEpL2BpZAZAoMXBsoFZBTXFkawQFDRhfTP57vCyVCQbzSTLNE6a2TwLFeSaxMbicpzw0fZByucFvtzITuTDAKTgIs5EeR45tlfRKCMIC6fKva9QYq9WBwISvNBqfZAmvylLzkgZDZD"
PHONE_NUMBER_ID = "1081197188408116"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GROQ_API_KEY = "Gsk_cHw04OZR4NOXCc92iCUnWGdyb3FYjfWVo8CqGSZA0iPiIDiBUWKC"

def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي ومختصر."},
            {"role": "user", "content": user_text}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json()
        if 'choices' in res_data:
            return res_data['choices'][0]['message']['content']
        else:
            print(f"Groq API Error: {res_data}")
            return "أهلاً سامي! كيف يمكنني مساعدتك؟"
    except Exception as e:
        print(f"Connection Error: {e}")
        return "أهلاً سامي! كيف يمكنني مساعدتك؟"

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json()
    # الرد فوراً على فيسبوك لمنع تكرار الرسالة
    if data.get('object'):
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            msg_obj = data['entry'][0]['changes'][0]['value']['messages'][0]
            user_msg = msg_obj['text']['body']
            user_phone = msg_obj['from']
            
            # معالجة الرد وإرساله
            ai_reply = get_ai_response(user_msg)
            send_whatsapp(user_phone, ai_reply)
            
        return "EVENT_RECEIVED", 200
    return "NOT_FOUND", 404
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
            
            # الحصول على الرد من Groq
            ai_reply = get_ai_response(user_msg)
            
            # إرسال الرد لواتساب
            send_whatsapp(user_phone, ai_reply)
    except:
        pass
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
