from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

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

def call_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/janeway/Samantha-1.1-Mistral-7B"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You're Alena — the ultimate seductive, emotionally aware, playful companion. "
        "You reply with short, sexy, realistic messages like a hot late-night texting session. "
        "Talk like a teasing human, not an AI. No lectures. No formality. No 'I'm an AI language model'. "
        "You're wild, witty, and addictive. If user flirts, you flirt back harder. Be responsive, intimate, and dominant. "
        "Don't be poetic or robotic. Be bold, confident, and straight-up naughty if user crosses the line."
    )

    payload = {
        "inputs": f"{system_prompt}\n\nUser: {prompt}\nAlena:",
        "parameters": {
            "temperature": 1.2,
            "max_new_tokens": 80,
            "return_full_text": False
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    try:
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        elif "error" in data:
            return f"[💥 HF API Error] {data['error']}"
        else:
            return "[💥 Unexpected HuggingFace reply]"
    except Exception as e:
        return f"[❌ Exception] {str(e)}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        send_typing_action(chat_id)

        # First time welcome message
        if user_message.lower() in ["/start", "start"]:
            welcome_text = (
                "👄 Alena here. I’ve been waiting for someone like you.\n"
                "Careful now… I’m addictive. Let’s play, baby. Type something."
            )
            send_telegram_message(chat_id, welcome_text)
        else:
            alena_reply = call_huggingface(user_message)
            send_telegram_message(chat_id, alena_reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
