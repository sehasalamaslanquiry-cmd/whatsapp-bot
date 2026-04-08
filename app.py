import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- بيانات الربط (تم الحفاظ عليها بدقة) ---
FB_TOKEN = "EAARkORIGoHIBROYnLBJOX0lRuEhSniOIdANZAv9ZCRWeNpnzti4Lu7RAyoimTCOZBvfW9SRNo6c6AlJvmrEI8b4uAyM5GF3eZCqjab2vz65d163FzV20hWrXICPh22SEVOGp0pZCpvpcPXLhb0RCm7kZAPZA4qtEwPT2wLSiPiKriLU0sKWe5XkyK9ZBs2YRah7nUQZDZD"
PHONE_NUMBER_ID = "1064201223444303"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GROQ_API_KEY = "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"

# --- دالة إرسال نسخة المراقبة ---
def send_monitoring_msg(sender_phone, user_msg, bot_response):
    admin_number = "967739704861" 
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": admin_number,
        "type": "text",
        "text": {"body": f"🔍 مراقبة جديدة:\n📱 رقم المرسل: {sender_phone}\n👤 رسالته: {user_msg}\n🤖 رد البوت: {bot_response}"}
    }
    requests.post(url, headers=headers, json=payload)

def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
                        {
                "role": "system", 
                "content": "أنت مساعد المهندس سامي المجيدي. جاوب باللهجة التعزية بذكاء واختصار شديد. إذا سألك أحد عن (إجازات مرضية) أو (أي وظيفة مساحة أو هندسة أو أخرى)، قله: 'أبشر يا غالي، سامي بيشتغلك على طول، بس ارسل بياناتك كاملة وما عليك'. إذا سألو عن (السعر أو التكلفة)، قله: 'السعر كالعادة، لا أنت وسامي وما بنختلف'، واسأله: 'تشتي رقمه المباشر؟'. إذا وافق، أعطيه هذا الرقم: 967739704861. إذا سألك شيء ما تعرفوش، قل: 'والله هذا ما بش معي خبر فيه، اسأل سامي أو راسله على رقمه المباشر'."
            },

            {"role": "user", "content": user_text}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json()
        return res_data['choices'][0]['message']['content'] if response.status_code == 200 else "أهلاً يا غالي، كيف أخدمك؟"
    except:
        return "عذراً يا طيب، حصل معي تشويش بسيط، أعد المحاولة."

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

                # --- أسطر المراقبة في Render (تم إصلاح المسافات هنا) ---
                print(f"\n--- 📥 رسالة جديدة استلمتها ---")
                print(f"👤 من رقم: {user_phone}")
                print(f"💬 محتوى الرسالة: {user_msg}")
                print(f"-------------------------------\n")

                # منع التكرار مع رقم المراقبة
                #if user_phone == "967739704861":
                  #  return "OK", 200

                ai_reply = get_ai_response(user_msg)
                
                # إرسال الرد للمستخدم
                send_whatsapp(user_phone, ai_reply)
                
                # إرسال تقرير المراقبة لك
                send_monitoring_msg(user_phone, user_msg, ai_reply)
    except Exception as e:
        print(f"حدث خطأ: {e}")
        
    return "OK", 200

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
