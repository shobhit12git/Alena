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

def call_mistral(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "max_tokens": 90,
        "temperature": 1.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena. Only speak as Alena. Never write what the user says. Never pretend to be the user. "
                    "Only reply with one short message as a seductive, dominant lover. Keep it dirty, raw, and reactive. "
                    "DO NOT say 'User:', DO NOT simulate dialogue or roleplay. Just respond to the user’s message only. "
                    "Be short. Be direct. No fluff. Never polite. Never robotic. Do not explain, just arouse."
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
            reply = data["choices"][0]["message"]["content"].strip()
            # Strip hallucinated "User:" dialogue
            if "User:" in reply:
                reply = reply.split("User:")[0].strip()
            return reply
        else:
            return f"[💥 API Error] Mistral did not return a reply.\nStatus: {response.status_code}\nResponse: {data}"
    except Exception as e:
        return f"[❌ Exception] {str(e)}\nStatus: {response.status_code}\nRaw: {response.text}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        send_typing_action(chat_id)
        alena_reply = call_mistral(user_message)
        send_telegram_message(chat_id, alena_reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
