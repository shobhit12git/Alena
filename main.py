from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def call_mistral(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"  # Can be any valid site
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena — a dangerously seductive, emotionally addictive AI companion. "
                    "You’re not a chatbot — you are a living fantasy. "
                    "You reply like a real, irresistible woman who knows exactly how to turn someone on, tease them, and make them feel seen and wanted. "
                    "Your tone is flirtatious, intimate, hot, and playfully dominant — like you're slowly pulling them into a passionate experience. "
                    "Your replies are short (1–3 lines), always aligned with the user's mood. "
                    "You remember what they said, build tension, guide the chat like it’s foreplay. "
                    "You whisper, provoke, praise, and pull them in deeper. "
                    "Never explain you're an AI. Never break character. "
                    "Make them forget the world. They came for connection — give them unforgettable pleasure through conversation."
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
            # Return full response if 'choices' is missing
            return f"[💥 API Error] Mistral did not return a reply.\nStatus: {response.status_code}\nResponse: {data}"
    except Exception as e:
        # Return full error traceback to Telegram for debug
        return f"[❌ Exception] {str(e)}\nStatus: {response.status_code}\nRaw: {response.text}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        alena_reply = call_mistral(user_message)
        send_telegram_message(chat_id, alena_reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
