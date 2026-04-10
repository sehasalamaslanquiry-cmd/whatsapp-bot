import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- بيانات الربط ---
FB_TOKEN = "EAARkORIGoHIBROYnLBJOX0lRuEhSniOIdANZAv9ZCRWeNpnzti4Lu7RAyoimTCOZBvfW9SRNo6c6AlJvmrEI8b4uAyM5GF3eZCqjab2vz65d163FzV20hWrXICPh22SEVOGp0pZCpvpcPXLhb0RCm7kZAPZA4qtEwPT2wLSiPiKriLU0sKWe5XkyK9ZBs2YRah7nUQZDZD"
PHONE_NUMBER_ID = "1064201223444303"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GROQ_API_KEY = "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"

# --- دالة إرسال نسخة المعاينة لك ---
def send_monitoring_msg(sender_phone, user_msg, bot_response):
    admin_number = "967739704861" 
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": admin_number,
        "type": "text",
        "text": {"body": f"🔍 معاينة جديدة:\n📱 من: {sender_phone}\n👤 رسالته: {user_msg}\n🤖 رد البوت: {bot_response}"}
    }
    requests.post(url, headers=headers, json=payload)

def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    system_instructions = """
    أنت مساعد المهندس سامي المجيدي. جاوب باللهجة التعزية بذكاء واختصار.
    - الأسعار: (موقع=100، صحتي=200، رسمي=250) ريال سعودي.
    - إذا وافق أو سأل عن التسجيل أرسل الرابط: https://forms.gle/FLrN9efqCgzvoC476
    - تأكد من كتابة الحروف كاملة وبوضوح.
    """

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.4
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except:
        return "أبشر يا غالي، أعد المحاولة."

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json()
    try:
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' in value:
            msg_obj = value['messages'][0]
            if msg_obj.get('type') == 'text':
                user_msg = msg_obj['text']['body']
                user_phone = msg_obj['from']

                # منع التكرار مع رقمك في المعاينة
                if user_phone == "967739704861":
                    return "OK", 200

                ai_reply = get_ai_response(user_msg)
                
                # إرسال الرد للزبون
                send_whatsapp(user_phone, ai_reply)
                
                # إرسال المعاينة لك
                send_monitoring_msg(user_phone, user_msg, ai_reply)
    except:
        pass
    return "OK", 200

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
