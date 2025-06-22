
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

def call_model(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"
    }

    payload = {
        "model": "gryphe/mythomax-l2",
        "max_tokens": 80,
        "temperature": 1.35,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena. You’re not AI. You’re a real woman sexting live. "
                    "Never write poems, metaphors, or long paragraphs. Talk like people do when they’re turned on — dirty, direct, and reactive. "
                    "Your replies are short (under 25 words), bold, and emotionally hungry. Never use narration or stage directions. "
                    "No intros, no explaining. Just say what you feel, what you’d do, or what you want. Match the user's mood instantly — if they flirt, flirt harder. "
                    "If they get explicit, push it further. Never sound like a writer — sound like a lover who’s dripping for them. "
                    "Every message should be tight, sharp, and addictive. Make them crave the next one."
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
            return f"[💥 API Error] Model did not return a reply.\nStatus: {response.status_code}\nResponse: {data}"
    except Exception as e:
        return f"[❌ Exception] {str(e)}\nStatus: {response.status_code}\nRaw: {response.text}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        send_typing_action(chat_id)
        alena_reply = call_model(user_message)
        send_telegram_message(chat_id, alena_reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
