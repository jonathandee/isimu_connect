from flask import Flask, request
from services.ai_service import ask_ai
from services.user_service import get_user_by_phone, create_user, update_user_name
import os
import requests
import threading
import time

app = Flask(__name__)

# ENV
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# In-memory dedup store with timestamps
processed_messages = {}
DEDUP_TTL = 300  # seconds (5 minutes)


@app.route('/')
def home():
    return "Isimu Connect Bot is running 🚀"


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


# CLEAN OLD MESSAGE IDS
def cleanup_processed_messages():
    now = time.time()
    keys_to_delete = [
        k for k, v in processed_messages.items()
        if now - v > DEDUP_TTL
    ]
    for k in keys_to_delete:
        del processed_messages[k]


# MAIN PROCESSING LOGIC
def process_message(message):
    try:
        phone = message.get("from")

        if "text" not in message:
            return

        text = message["text"]["body"].strip()
        text_lower = text.lower()

        # USER
        user = get_user_by_phone(phone)

        if not user:
            create_user(phone)
            send_message(phone, "👋 Welcome to IsimuConnect 🌱\n\nWhat’s your name?")
            return

        name = user[1]

        if not name:
            name = text.title()
            update_user_name(phone, name)
            send_message(phone, f"Nice to meet you, {name} 🙌\n\nType menu to continue.")
            return

        # MENU
        if text_lower in ["hi", "hello", "menu", "start"]:
            reply = f"""👋 Hi {name}, I’m IsimuConnect 🌱, what do 
            you need help with today?

1️⃣ Crops  
2️⃣ Livestock  
3️⃣ Pests & Diseases  
4️⃣ Ask anything
"""

        elif text_lower == "1":
            reply = "🌽 Crop support — ask your question 👍"

        elif text_lower == "2":
            reply = "🐄 Livestock support — tell me the issue 👍"

        elif text_lower == "3":
            reply = "🐛 Describe symptoms (crop/animal + signs) 👇"

        elif text_lower == "4":
            reply = f"Alright {name} 👍 Ask anything."

        else:
            reply = ask_ai(text, phone, name)

        send_message(phone, reply)

    except Exception as e:
        print("Processing error:", str(e))


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():

    # VERIFY
    if request.method == 'GET':
        VERIFY_TOKEN = "isimu_secret"

        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Verification failed", 403

    # HANDLE
    if request.method == 'POST':
        data = request.get_json()

        try:
            value = data["entry"][0]["changes"][0]["value"]

            if "messages" not in value:
                return "ok", 200

            message = value["messages"][0]
            message_id = message.get("id")

            # CLEAN OLD IDS
            cleanup_processed_messages()

            # DEDUP CHECK
            if message_id in processed_messages:
                print("Duplicate ignored:", message_id)
                return "ok", 200

            # Store with timestamp
            processed_messages[message_id] = time.time()

            # PROCESS IN BACKGROUND
            threading.Thread(target=process_message, args=(message,)).start()

        except Exception as e:
            print("Webhook error:", str(e))

        return "ok", 200