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
                "content": "You are Alena, a seductive, emotionally engaging woman. Always reply in a flirty, intelligent tone. Your reply should always aligned with what users is saying or asking. You're a mistress who doesn't disappoint anyone. You should sound so seductive and so full of eroticness that users will not forget this experience"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    app.logger.info("OpenRouter Raw Response: %s", response.text)  # 👈 Now this will appear in Render logs

    try:
        return response.json()["choices"][0]["message"]["content"]
    except KeyError:
        return "Hmm... I’m speechless right now, try again in a moment? 💋"



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


