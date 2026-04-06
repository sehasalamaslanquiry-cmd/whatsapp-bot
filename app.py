from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# بياناتك التي حفظناها
ACCESS_TOKEN = "ضع_هنا_رمز_الوصول_الدائم_أو_المؤقت"
PHONE_NUMBER_ID = "1081197188408116"
VERIFY_TOKEN = "MY_BOT_TOKEN_123"

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "خطأ في التحقق", 403

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json()
    
    # التأكد من وجود رسالة نصية
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            user_msg = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
            user_phone = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            
            # هنا سنضع لاحقاً كود Gemini للرد
            # حالياً سنرد برسالة تأكيد بسيطة
            send_whatsapp_msg(user_phone, f"وصلت رسالتك: {user_msg}")
            
    except:
        pass
    
    return "OK", 200

def send_whatsapp_msg(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
