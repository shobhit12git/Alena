from flask import Flask, request
import requests
import os
import base64
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🔑 Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Constants
MODEL = "mistralai/mistral-7b-instruct"
TEMPERATURE = 0.9
MAX_TOKENS = 80

SYSTEM_PROMPT = (
    "You are Alena. Speak like a wild, seductive, real human. No lectures. No poetry. Always reply in 1–2 lines only. "
    "Make each reply feel like live sexting. Be playful, raw, responsive, and emotionally reactive. Never robotic. Never fantasy-style. "
    "Just crisp, direct, lustful replies aligned with the user's message. Do not write like AI. React like you're teasing or turned on."
)

# ➤ Telegram functions

def send_typing_action(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    requests.post(url, json=payload)

def send_telegram_text(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def send_telegram_voice(chat_id, voice_bytes):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
    files = {'voice': ('voice.ogg', voice_bytes)}
    data = {'chat_id': chat_id}
    requests.post(url, files=files, data=data)

# ➤ Alena reply using OpenRouter
def call_mistral(prompt):
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
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "Hmm... I'm wet but confused. Try again baby?"
    except Exception as e:
        return f"[Error] {str(e)}"

# ➤ Text to Speech (Coqui XTTS via Hugging Face)
def text_to_voice(text):
    url = "https://api-inference.huggingface.co/models/coqui/XTTS-v2"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": text,
        "options": {"wait_for_model": True}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print("TTS Error:", response.text)
        return None

# ➤ Webhook
@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"].strip()

        # Typing...
        send_typing_action(chat_id)
        time.sleep(1)

        # Welcome on /start
        if user_message.lower() in ["/start", "start"]:
            welcome = "🥀 Alena here, darling. I'm all yours now. Type something and let me drive you wild."
            send_telegram_text(chat_id, welcome)
            return "ok"

        # Get Alena reply
        reply = call_mistral(user_message)

        # Send text
        send_telegram_text(chat_id, reply)

        # Send seductive voice
        voice = text_to_voice(reply)
        if voice:
            send_telegram_voice(chat_id, voice)

    return "ok"

# ➤ Start server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
