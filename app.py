import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- بيانات الربط (تم الحفاظ عليها) ---
FB_TOKEN = "EAARkORIGoHIBROYnLBJOX0lRuEhSniOIdANZAv9ZCRWeNpnzti4Lu7RAyoimTCOZBvfW9SRNo6c6AlJvmrEI8b4uAyM5GF3eZCqjab2vz65d163FzV20hWrXICPh22SEVOGp0pZCpvpcPXLhb0RCm7kZAPZA4qtEwPT2wLSiPiKriLU0sKWe5XkyK9ZBs2YRah7nUQZDZD"
PHONE_NUMBER_ID = "1064201223444303"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"
GROQ_API_KEY = "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"

# --- القوائم الذكية ---
REQUIRED_DATA = """
⬇️ ارســــــــــــــل البيــانات ⬇️
 
1-الاسم الرباعي: 
2-رقم الهوية: 
3-تاريخ الميلاد:
4-الجنسية: 
5-الجنس: 
7-جهة العمل: 
8-اسم المهنة: 
9-تاريخ الاجازه:
10-المدينة:
"""

def get_ai_response(user_text):
def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # دمج الرابط الخاص بك في التعليمات
    system_instructions = """
    أنت مساعد المهندس سامي المجيدي. جاوب باللهجة التعزية بذكاء.
    
    - قواعد الأسعار:
      1. (موقع وهمي) = 100 ريال سعودي.
      2. (صحتي الرسمي) = 200 ريال سعودي.
      3. (مزور) = 250 ريال سعودي.
    
    - إذا وافق الزبون على السعر أو قال (كيف أسجل؟) أو (أرسل البيانات)، قله:
      'أبشر يا غالي، من عيوني.. ادخل عبي بياناتك كاملة في هذا الرابط واعتمد الطلب وبنتواصل معك فوراً: https://forms.gle/FLrN9efqCgzvoC476'
    
    - إذا سأل عن (السعر بشكل عام)، قله: 'معنا أنواع (موقع وهمي، صحتي الرسمي، مزور)، أي واحد تشتي أعطيك سعره؟'.
    - لا تكرر الكلام، كن مختصراً، وتأكد أن الحروف كاملة.
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
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json()
        return res_data['choices'][0]['message']['content']
    except:
        return "أبشر يا غالي، بس حصل تشويش بسيط، أعد إرسال سؤالك."

# --- بقية الكود (المراقبة والاستقبال) ---
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

                print(f"\n--- 📥 رسالة من: {user_phone} ---\n💬 المحتوى: {user_msg}\n")

                #if user_phone == "967739704861":
                   # return "OK", 200

                ai_reply = get_ai_response(user_msg)
                send_whatsapp(user_phone, ai_reply)
    except: pass
    return "OK", 200

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
