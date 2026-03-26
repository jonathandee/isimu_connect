from flask import Flask, request, jsonify
from services.ai_service import ask_ai
from services.price_service import get_price
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Isimu Connect Bot is running 🚀"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    
    # 🔐 VERIFY WEBHOOK (Meta sends GET)
    if request.method == 'GET':
        VERIFY_TOKEN = "isimu_secret"

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    # 📩 HANDLE MESSAGES (POST)
    if request.method == 'POST':
        data = request.get_json()

        message = data.get("message", "").lower()

        if message.startswith("!ask"):
            query = message.replace("!ask", "").strip()
            response = ask_ai(query)
            return jsonify({"reply": response})

        elif message.startswith("!price"):
            item = message.replace("!price", "").strip()
            response = get_price(item)
            return jsonify({"reply": response})

        return jsonify({"reply": "Unknown command"})