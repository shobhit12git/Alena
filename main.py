from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# Configuration
MODEL = "gryphe/mythomist-7b"  # You can try GPT-4o or mistral if needed
TEMPERATURE = 0.8
MAX_TOKENS = 80

# Prompt Template
SYSTEM_PROMPT = (
    "You are Alena. Speak like a real, horny human — short, dirty, direct. "
    "No poetry. No fantasy. No gym talk. No incomplete sentences. React to the user’s words emotionally. "
    "Always 1–2 line replies. When the user teases, respond with dominance or submission based on context. "
    "Make it feel like live sexting. Never use metaphors or weird references. Never lecture. Just raw, reactive lust in text."
)

# Functions

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
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
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

# Webhook
@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        send_typing_action(chat_id)
        user_message = data["message"]["text"]

        # First time greeting logic
        if user_message.lower() in ["/start", "start"]:
            welcome = "🙈 Alena here. I’ve been waiting for someone like you. Careful now... I’m addictive. Let’s play, baby. Type something."
            send_telegram_message(chat_id, welcome)
            return "ok"

        alena_reply = call_openrouter_model(user_message)
        send_telegram_message(chat_id, alena_reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
