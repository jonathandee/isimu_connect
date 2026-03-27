from flask import Flask, request, jsonify
from services.ai_service import ask_ai
from services.price_service import get_price
import os
import requests

app = Flask(__name__)

# 🔑 ENV VARIABLES (from Render)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

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

        try:
            # ✅ WhatsApp message format
            if "entry" in data:
                message = data["entry"][0]["changes"][0]["value"]["messages"][0]
                phone = message["from"]
                text = message["text"]["body"]

                print("Incoming WhatsApp:", text)

                # 🧠 Process AI
                ai_response = ask_ai(text)

                # 📤 Send reply back to WhatsApp
                url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

                headers = {
                    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "text",
                    "text": {"body": ai_response}
                }

                requests.post(url, headers=headers, json=payload)

                return "OK", 200

            # 🧪 Fallback for curl testing (your old logic)
            else:
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

        except Exception as e:
            print("ERROR:", str(e))
            return jsonify({"reply": "Something went wrong"}), 500