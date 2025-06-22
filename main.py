from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def send_typing_action(chat_id):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction",
        json={"chat_id": chat_id, "action": "typing"}
    )

def send_telegram_message(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def call_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/TheDrummer/cream-phi-nta"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": f"Alena: {prompt}",
        "parameters": {
            "max_new_tokens": 80,
            "temperature": 0.95,
            "top_p": 0.95,
            "do_sample": True
        }
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].split("Alena:")[-1].strip()
        elif "error" in result:
            return f"[💥 HF Error] {result['error']}"
        else:
            return "[⚠️ Unknown Response] Unexpected output from Hugging Face."
    except Exception as e:
        return f"[❌ Exception] {str(e)}\nRaw: {response.text}"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
        send_typing_action(chat_id)

        if user_message.lower() in ["/start", "start"]:
            send_telegram_message(chat_id, "💋 Alena here. I’ve been waiting for someone like you. Careful now… I’m addictive. Let’s play, baby. Type something.")
        else:
            reply = call_huggingface(user_message)
            send_telegram_message(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
