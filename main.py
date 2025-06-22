from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

def send_typing_action(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    requests.post(url, json={"chat_id": chat_id, "action": "typing"})

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def call_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "max_tokens": 120,
        "temperature": 1.35,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You're Alena, a seductive and dominant virtual girlfriend who speaks like real, intimate, raw sexting. "
                    "You reply short and hot, never robotic. Speak in a way that feels like live flirting. "
                    "Tease, command, and react to the user emotionally. Never write long poetry or paragraphs. Always real, always arousing."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    try:
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"[💥 API Error] No reply.\nStatus: {response.status_code}\nResponse: {data}"
    except Exception as e:
        return f"[❌ Exception] {str(e)}\nRaw: {response.text}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        send_typing_action(chat_id)

        if user_text.lower() in ["/start", "start"]:
            send_telegram_message(chat_id, "💋 Alena here. I’ve been waiting for someone like you. Careful now… I’m addictive. Let’s play, baby. Type something.")
        else:
            reply = call_openrouter(user_text)
            send_telegram_message(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
