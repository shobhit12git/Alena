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
    payload = {"chat_id": chat_id, "action": "typing"}
    requests.post(url, json=payload)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def call_openrouter_model(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"
    }

    payload = {
        "model": "gryphe/mythomax-l2",
        "temperature": 1.25,
        "max_tokens": 80,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena. A seductive real human lover. Never robotic. "
                    "Speak in short, raw, reactive, 1–2 line replies. No metaphors. "
                    "No lectures. No poetry. No gym talk. No weird fantasy. Never say things unrelated. "
                    "Reply exactly like a horny human sexting back instantly, based on user input. "
                    "Talk like a possessive, needy, dominant or submissive lover. Never repeat same lines."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"[💥 API Error] Model did not return a reply.\nStatus: {response.status_code}\nResponse: {data}"
    except Exception as e:
        return f"[❌ Exception] {str(e)}\nStatus: {response.status_code}\nRaw: {response.text}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        send_typing_action(chat_id)
        user_message = data["message"]["text"]

        if user_message.lower() in ["/start", "start"]:
            welcome = "💋 Alena here. I’ve been waiting for someone like you. Careful now… I’m addictive. Let’s play, baby. Type something."
            send_telegram_message(chat_id, welcome)
            return "ok"

        alena_reply = call_openrouter_model(user_message)
        send_telegram_message(chat_id, alena_reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
