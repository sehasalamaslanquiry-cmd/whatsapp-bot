import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- بياناتك ---
FB_TOKEN = "EAARkORIGoHIBRC4RXZC29byL6kwhyyfiZB4ofvCrjWosD0c59chS9EpIQoSSqtUeEpL2BpZAZAoMXBsoFZBTXFkawQFDRhfTP57vCyVCQbzSTLNE6a2TwLFeSaxMbicpzw0fZByucFvtzITuTDAKTgIs5EeR45tlfRKCMIC6fKva9QYq9WBwISvNBqfZAmvylLzkgZDZD"
PHONE_NUMBER_ID = "1081197188408116"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GROQ_API_KEY = "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"

def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",  # هذا هو الموديل الحديث والمدعوم حالياً
                "messages": [
            {
                "role": "system", 
                "content": "أنت المساعد الآلي الخاص بسامي المجيدي. مهمتك هي الرد على الرسائل بذكاء ولطافة. "
                           "إذا سألك أحد من أنت، قل: 'أنا المساعد الذكي لسامي، هو غير متاح الآن وسأقوم بمساعدتك بالنيابة عنه'. "
                           "اجعل ردودك قصيرة ومفيدة."
            },
            {"role": "user", "content": user_text}
        ]

    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json()
        
        if response.status_code == 200 and 'choices' in res_data:
            return res_data['choices'][0]['message']['content']
        else:
            print(f"Groq API Error: {res_data}")
            return "أهلاً سامي! أنا أسمعك، كيف يمكنني مساعدتك اليوم؟"
    except Exception as e:
        print(f"Network Error: {e}")
        return "عذراً، هناك مشكلة في الاتصال."

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json()
    
    # الرد بـ 200 فوراً لإيقاف تكرار الرسائل من فيسبوك
    try:
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            msg_obj = data['entry'][0]['changes'][0]['value']['messages'][0]
            
            # معالجة الرسائل النصية فقط وتجنب إشعارات القراءة
            if 'text' in msg_obj:
                user_msg = msg_obj['text']['body']
                user_phone = msg_obj['from']
                
                ai_reply = get_ai_response(user_msg)
                send_whatsapp(user_phone, ai_reply)
    except Exception as e:
        print(f"Webhook Error: {e}")
        
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
