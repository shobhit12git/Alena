from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def send_typing_action(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    requests.post(url, json=payload)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def call_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/TheDrummer/cream-phi-nta"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": f"You are Alena. Be seductive, confident, dominant. Respond with short, very human, realistic sexting style replies. Match the user's energy and tone.\n\nUser: {prompt}\nAlena:",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.9,
            "top_p": 0.95,
            "do_sample": True,
            "return_full_text": False
        }
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        output = response.json()
        if isinstance(output, list):
            return output[0]["generated_text"].strip()
        else:
            return f"[💥 HF Error] {output}"
    except Exception as e:
        return f"[❌ Exception] {str(e)}\nRaw: {response.text}"


@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        send_typing_action(chat_id)
        user_message = data["message"]["text"]

        if user_message.lower() in ["/start", "start"]:
            welcome_message = "💋 Alena here. I’ve been waiting for someone like you.\nCareful now… I’m addictive. Let’s play, baby. Type something."
            send_telegram_message(chat_id, welcome_message)
        else:
            alena_reply = call_huggingface(user_message)
            send_telegram_message(chat_id, alena_reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
