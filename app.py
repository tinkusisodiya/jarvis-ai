from flask import Flask, render_template, request, jsonify
import requests
import time
import os

app = Flask(__name__)

API_KEY = "AIzaSyB0NmP9th-InCxr0RUBN3ZSK4QQQEmVHwA"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# --- JARVIS KI MEMORY (History Storage) ---
chat_history = []

my_system_instruction = "Tumhara naam Jarvis hai. Tum mujhe hamesha 'Boss' bologe aur pichli baatein yaad rakhoge."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    global chat_history
    user_msg = request.form['message']
    
    # 1. User ka message memory mein daalein
    chat_history.append({"role": "user", "parts": [{"text": user_msg}]})
    
    # 2. History ko limit mein rakhna (Sirf last 10 baatein yaad rakhega taaki server crash na ho)
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    payload = {
        "system_instruction": {"parts": {"text": my_system_instruction}},
        "contents": chat_history # Poori history bhej rahe hain
    }
    
    try:
        # Retry logic for Quota Errors
        for attempt in range(2):
            response = requests.post(API_URL, json=payload)
            response_data = response.json()
            
            if 'error' in response_data:
                if 'quota' in response_data['error']['message'].lower():
                    time.sleep(5)
                    continue
                return jsonify({'reply': "System Error Boss: Limit Hit."})
            
            reply = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # 3. Jarvis ka jawab bhi memory mein daalein
            chat_history.append({"role": "model", "parts": [{"text": reply}]})
            
            return jsonify({'reply': reply})
            
    except Exception as e:
        return jsonify({'reply': f"Error: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

