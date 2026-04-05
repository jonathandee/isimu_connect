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


from flask import request
import requests
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def send_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    requests.post(url, headers=headers, json=data)


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

    # HANDLE MESSAGES
    if request.method == 'POST':
        data = request.get_json()

        try:
            value = data["entry"][0]["changes"][0]["value"]

            # Ignore non-message events (VERY IMPORTANT)
            if "messages" not in value:
                return "ok", 200

            message = value["messages"][0]
            phone = message["from"]
            text = message["text"]["body"].strip().lower()

            # MENU LOGIC
            if text in ["hi", "hello", "menu", "start"]:
                reply = """👋 Hi, I’m IsimuConnect 🌱

What would you like help with?

1️⃣ 🌽 Crops  
2️⃣ 🐄 Livestock  
3️⃣ 🐛 Pests & Diseases  
4️⃣ 💬 Ask Something else
"""

            elif text == "1":
                reply = """🌽 Crop Support

What do you need help with?

• Planting  
• Fertilizer  
• Diseases  
• Yields  

Type your question 👇
"""

            elif text == "2":
                reply = """🐄 Livestock Support

What do you need help with?

• Feeding  
• Diseases  
• Breeding  
• Housing  

Describe your issue 👇
"""

            elif text == "3":
                reply = """🐛 Pest & Disease Help

Tell me:

• Crop or animal  
• Symptoms  

Example:
"My maize leaves are yellow"

👇 Go ahead
"""

            elif text == "4":
                reply = "Alright 👍 Ask me anything about your farm."

            else:
                # 🤖 FALLBACK TO AI
                from services.ai_service import ask_ai
                reply = ask_ai(text, phone)

            # 📤 SEND RESPONSE
            send_message(phone, reply)

        except Exception as e:
            print("Webhook error:", str(e))

        return "ok", 200

    # HANDLE WHATSAPP MESSAGES
    if request.method == 'POST':
        data = request.get_json()

        try:
            if "entry" in data:
                message = data["entry"][0]["changes"][0]["value"]["messages"][0]

                phone = message["from"]
                text = message["text"]["body"].strip()

                user = get_user_by_phone(phone)
                name = user[1] if user else None

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
                    reply = ask_ai(text, phone, name)

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