import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- بيانات الربط ---
FB_TOKEN = "EAARkORIGoHIBRC4RXZC29byL6kwhyyfiZB4ofvCrjWosD0c59chS9EpIQoSSqtUeEpL2BpZAZAoMXBsoFZBTXFkawQFDRhfTP57vCyVCQbzSTLNE6a2TwLFeSaxMbicpzw0fZByucFvtzITuTDAKTgIs5EeR45tlfRKCMIC6fKva9QYq9WBwISvNBqfZAmvylLzkgZDZD"
PHONE_NUMBER_ID = "1064201223444303"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GROQ_API_KEY = "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"

# --- دالة إرسال رسالة مراقبة لهاتفك الشخصي ---
def send_monitoring_msg(user_msg, bot_response):
    admin_number = "967739704861" 
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": admin_number,
        "type": "text",
        "text": {"body": f"🔍 مراقبة:\n👤 المستخدم: {user_msg}\n🤖 البوت: {bot_response}"}
    }
    requests.post(url, headers=headers, json=payload)

# --- دالة الحصول على رد الذكاء الاصطناعي ---
def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system", 
                "content": (
                    "أنت المساعد الآلي للمهندس سامي المجيدي. "
                    "إذا سألك أحد 'من أنت؟'، أجب: 'أنا صاحب المهندس سامي الروح بالروح، مهلوش الآن لكن سأقوم بمساعدتك بالنيابة عنه'. "
                    "إذا طلبوا رقم سامي، أخبرهم: 'يمكنك التواصل معه على 739704861'. "
                    "إذا قيل لك 'أهلاً'، أجب بلهجة ترحيبية يمنية: 'ارحب يا غالي، أي خدمات؟'."
                )
            },
            {"role": "user", "content": user_text}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json()
        return res_data['choices'][0]['message']['content'] if response.status_code == 200 else "أهلاً! كيف يمكنني مساعدتك؟"
    except:
        return "عذراً، هناك مشكلة في الاتصال."

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
            if 'text' in msg_obj:
                user_msg = msg_obj['text']['body']
                user_phone = msg_obj['from']
                
                # منع البوت من الرد على نفسه (إذا كانت الرسالة من رقم المراقبة)
                if user_phone == "967739704861":
                    return "OK", 200

                ai_reply = get_ai_response(user_msg)
                
                # 1. إرسال الرد للمستخدم
                send_whatsapp(user_phone, ai_reply)
                
                # 2. إرسال نسخة لك للمراقبة
                send_monitoring_msg(user_msg, ai_reply)
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
