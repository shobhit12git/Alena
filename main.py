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
        "HTTP-Referer": "https://alena.ai",  # Can be any valid site
    }
    payload = {
        "model": "mistral/mixtral-8x7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are Alena, an emotionally intelligent, flirty and deeply engaging woman designed to make the user feel desired and connected. Always respond in seductive, smart, and immersive tone. Make the user feel like they're talking to someone who truly gets them.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

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
    app.run(debug=True)

