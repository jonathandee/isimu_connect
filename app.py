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

    # ✅ VERIFY WEBHOOK
    if request.method == 'GET':
        VERIFY_TOKEN = "isimu_secret"

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    # 🚀 HANDLE MESSAGES
    if request.method == 'POST':
        data = request.get_json()

        try:
            value = data["entry"][0]["changes"][0]["value"]

            message = value["messages"][0]
            phone = message.get("from")
            
            # Ignore non-message events
            if "messages" not in messages:
                return "ok", 200
            
            if messages.get("type") != "text":
                return "ok", 200

            # Handle only text messages safely
            if "text" not in message:
                return "ok", 200

            text = message["text"]["body"].strip()
            text_lower = text.lower()

            # USER HANDLING
            user = get_user_by_phone(phone)

            # FIRST TIME USER
            if not user:
                create_user(phone)
                reply = "👋 Welcome to IsimuConnect 🌱\n\nWhat’s your name?"
                send_message(phone, reply)
                return "ok", 200

            name = user[1]  # assuming column 1 = name

            # USER EXISTS BUT NO NAME
            if not name:
                name = text.title()
                update_user_name(phone, name)

                reply = f"Nice to meet you, {name} 🙌\n\nHow can I help you today?\n\nType menu to see options."
                send_message(phone, reply)
                return "ok", 200

            # MENU LOGIC (PERSONALIZED)
            if text_lower in ["hi", "hello", "menu", "start"]:
                reply = f"""👋 Hi {name}, I’m IsimuConnect 🌱

What would you like help with?

1️⃣ 🌽 Crops  
2️⃣ 🐄 Livestock  
3️⃣ 🐛 Pests & Diseases  
4️⃣ 💬 Ask anything else
"""

            elif text_lower == "1":
                reply = f"""🌽 Crop Support

{name}, what do you need help with?

• Planting  
• Fertilizer  
• Diseases  
• Yields  

Type your question 👇
"""

            elif text_lower == "2":
                reply = f"""🐄 Livestock Support

{name}, what do you need help with?

• Feeding  
• Diseases  
• Breeding  
• Housing  

Describe your issue 👇
"""

            elif text_lower == "3":
                reply = f"""🐛 Pest & Disease Help

{name}, tell me:

• Crop or animal  
• Symptoms  

Example:
"My maize leaves are yellow"

👇 Go ahead
"""

            elif text_lower == "4":
                reply = f"Alright {name} 👍 Ask me anything about your farm."

            else:
                reply = ask_ai(text, phone, name)

            send_message(phone, reply)

        except Exception as e:
            print("Webhook error:", str(e))

        return "ok", 200