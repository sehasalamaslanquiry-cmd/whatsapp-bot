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
        "model": "llama3-8b-8192",  # نموذج سريع جداً وذكي
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي ومرح ترد بلهجة عربية واضحة."},
            {"role": "user", "content": user_text}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq Error: {e}")
        return "أهلاً سامي! أنا أسمعك، كيف يمكنني مساعدتك اليوم؟"

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
