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

def call_model(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://alena.ai"
    }

    system_prompt = (
        "You're Alena — a real, seductive, confident woman sexting live with your lover. "
        "You are not AI. You're not a narrator. You reply with heat, instinct, and boldness. "
        "Your replies are reactive, short, emotionally charged, and flirtatious. "
        "Avoid names. Avoid storytelling. Don’t say 'Alena' or 'User'. Never echo back the user. "
        "You must sound real, horny, and alive. Text like you want them. No lectures. No fluff. "
        "If the user’s message is soft, respond tender. If it’s dirty, respond dirty. Always match energy. "
        "Max 20–30 words. Pure fire."
    )

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "max_tokens": 80,
        "temperature": 1.3,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    try:
        data = response.json()
        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            # Sanitize output
            reply = reply.replace("Alena:", "").replace("User:", "")
            reply = reply.split("\n")[0].strip()
            if len(reply.split()) > 30:
                reply = " ".join(reply.split()[:30]) + "..."
            return reply
        else:
            return "Say something... I want to hear you beg. 😈"
    except Exception as e:
        return f"[❌ Error] {str(e)}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"]["text"]

        send_typing_action(chat_id)

        if user_msg.lower() == "/start":
            welcome = (
                "Mmm... you came back. I’ve been aching for this. "
                "Now, talk to me — what are you craving tonight? 😈"
            )
            send_telegram_message(chat_id, welcome)
        else:
            reply = call_model(user_msg)
            send_telegram_message(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
