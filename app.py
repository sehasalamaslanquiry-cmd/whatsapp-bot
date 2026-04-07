def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": user_text}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        res_data = response.json()
        
        # التأكد من وجود المفتاح بالإنجليزية 'choices'
        if 'choices' in res_data and len(res_data['choices']) > 0:
            return res_data['choices'][0]['message']['content']
        else:
            print(f"Groq Detail: {res_data}") # لمتابعة السبب في سجلات Render
            return "أهلاً سامي! كيف يمكنني مساعدتك؟"
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return "أهلاً سامي! كيف يمكنني مساعدتك؟"

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json()
    
    # التحقق من أن الرسالة ليست تكراراً أو إشعاراً بالقراءة
    try:
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            msg_obj = entry['messages'][0]
            user_msg = msg_obj.get('text', {}).get('body')
            user_phone = msg_obj.get('from')
            
            if user_msg:
                ai_reply = get_ai_response(user_msg)
                send_whatsapp(user_phone, ai_reply)
    except:
        pass
        
    # الرد بـ 200 فوراً لإيقاف فيسبوك عن إعادة إرسال نفس الرسالة
    return "OK", 200
