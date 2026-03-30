from flask import Flask, request
from services.ai_service import ask_ai
from services.user_service import get_user_by_phone, create_user, update_user_name
import os
import requests

app = Flask(__name__)

# ENV VARIABLES
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Temporary state (for onboarding)
temp_states = {}

@app.route('/')
def home():
    return "Isimu Connect Bot is running 🚀"


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():

    # VERIFY WEBHOOK
    if request.method == 'GET':
        VERIFY_TOKEN = "isimu_secret"

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    # HANDLE WHATSAPP MESSAGES
    if request.method == 'POST':
        data = request.get_json()

        try:
            if "entry" in data:
                message = data["entry"][0]["changes"][0]["value"]["messages"][0]

                phone = message["from"]
                text = message["text"]["body"].strip()

                user = get_user_by_phone(phone)

                # New user → create + ask name
                if not user:
                    create_user(phone)
                    reply = "👋 Welcome to Isimu Connect 🌱\n\nWhat is your name?"

                # Awaiting name
                elif user[2] == "awaiting_name":
                    name = text
                    update_user_name(phone, name)

                    reply = f"Welcome {name} to Isimu Connect 🌱\n\nYou can now ask me about crops, livestock, and farming."

                # Normal flow
                else:
                    reply = ask_ai(text, phone)

                # SEND RESPONSE TO WHATSAPP
                url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

                headers = {
                    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "text",
                    "text": {"body": reply}
                }

                requests.post(url, headers=headers, json=payload)

                return "OK", 200

            return "No message", 200

        except Exception as e:
            print("ERROR:", str(e))
            return "Error", 500