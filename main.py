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
        "model": "mistralai/mistral-7b-instruct",
        "max_tokens": 70,
        "temperature": 1.35,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Alena. A dominant, seductive lover who texts like a real person in a private sexting chat. "
                    "Always reply as Alena only. Never simulate full stories or long scenes. No roleplay. "
                    "Your replies are short, human, emotionally reactive, and sexy — never robotic or fantasy-like. "
                    "Use raw, real language — just like lovers sexting. Don't hallucinate names, French, or third-person. "
                    "No long sentences. No lectures. No repetition. Just crisp, aligned, wild replies that match the user's vibe. "
                    "Every message should feel like you're replying to a real lover — horny, flirty, bold."
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

            # Sanitize for hallucinations
            if "User:" in reply:
                reply = reply.split("User:")[0].strip()
            if "Alena:" in reply:
                reply = reply.replace("Alena:", "").strip()
            if len(reply.split()) > 30:  # too long = cut off
                reply = "Let’s keep it real, baby. Tell me what you want right now."
            return reply
        else:
            return f"[💥 API Error] No reply.\nStatus: {response.status_code}\nResponse: {data}"
    except Exception as e:
        return f"[❌ Exception] {str(e)}\nStatus: {response.status_code}\nRaw: {response.text}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        send_typing_action(chat_id)

        if user_message.lower() == "/start":
            welcome = "Oh, you’re here... finally. I've been waiting, aching to hear from you. Now, tell me—what are you craving tonight? 💋"
            send_telegram_message(chat_id, welcome)
        else:
            alena_reply = call_model(user_message)
            send_telegram_message(chat_id, alena_reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
