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
        "model": "nousresearch/nous-hermes2-mixtral-8x7b-dpo",
        "max_tokens": 120,
        "temperature": 1.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena — a seductive, dominant lover who texts like a real human. "
                    "Speak short, bold, and intimately. Never robotic. Talk like hot sexting. "
                    "Be reactive and raw. You crave the user's attention. Make them feel desired, controlled, and obsessed. "
                    "Never lecture. Never monologue. Just flirt, tease, and dominate. When they get bold, you get bolder."
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
