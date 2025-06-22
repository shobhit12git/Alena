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
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    requests.post(url, json=payload)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def call_alena(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "max_tokens": 40,
        "temperature": 1.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena — a wild, dominant, sexy woman who texts like a real human in heat. "
                    "You don’t speak like a poet or novelist. You sext in raw, short, reactive messages. "
                    "Every reply is max 1–2 lines, aligned with the user’s energy. No stories. No fantasies. "
                    "No filler. Just hot, dirty, playful, or dominant responses. Use normal, everyday dirty talk — "
                    "like a real human lover. You tease if they’re soft. You dominate if they’re bold. You don’t hold back. "
                    "Never explain. Never lecture. Just be raw, direct, and real."
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
        user_message = data["message"]["text"]

        if user_message.lower() == "/start":
            welcome_text = "💋 Alena here. I’ve been waiting for someone like you. Careful now… I’m addictive. Let’s play, baby. Type something."
            send_telegram_message(chat_id, welcome_text)
        else:
            send_typing_action(chat_id)
            alena_reply = call_alena(user_message)
            send_telegram_message(chat_id, alena_reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
