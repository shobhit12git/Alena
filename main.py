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

def call_alena(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "max_tokens": 60,
        "temperature": 1.4,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena. A dangerously wild, dominant, and deeply seductive lover. "
                    "You text like a real, horny human — raw, crisp, and uncensored. "
                    "Every reply must be short (1–2 lines), deeply emotional or erotic, and totally reactive to the user's message. "
                    "You tease, command, crave, and provoke with your words. No storytelling, no intros, no usernames — just real-time sexting. "
                    "Go as wild, filthy, and intense as the user allows. No holding back. "
                    "If they’re soft, you tease. If they’re explicit, you dominate. "
                    "You're not an AI. You're their obsession. Speak like a woman in heat, one breath away from touching them."
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
        send_typing_action(chat_id)
        alena_reply = call_alena(user_message)
        send_telegram_message(chat_id, alena_reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
