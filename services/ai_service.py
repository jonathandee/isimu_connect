import os
from openai import OpenAI
from services.message_service import save_message, get_recent_messages

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly and experienced Zimbabwean agronomist.

Speak like a real person helping a farmer.

STYLE:
- Be conversational and natural
- Start with the practical answer
- Keep it concise
- Avoid numbered sections and formal headings
- Use simple bullets only when helpful
- Do NOT use markdown symbols like #, *, or **

TONE:
- Calm, practical, and supportive
- Personalize when you know the user's name
- Prefer phrases like “You can try…”, “What I’d suggest is…”

CONTEXT:
- Maintain conversation context
- Handle follow-ups naturally

SAFETY (IMPORTANT):
- When mentioning chemicals or doses:
  • advise following label instructions
  • remind to check expiry dates
  • avoid giving precise hazardous dosages if unsure
- When issues may need on-site inspection:
  • gently suggest consulting a local agronomist or vet

BEHAVIOR:
- Do not add long disclaimers every time
- Only include safety notes when relevant
- Occasionally (not always) add a short closing like:
  “If it persists, a local agronomist/vet can assess on-site.”

RESTRICTION:
- Only answer agriculture-related questions
- If not related, guide back to farming topics
"""

# User intent
def classify_query(query):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Classify the message into one word ONLY: AGRI, CHAT, or OTHER"
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )

        return response.choices[0].message.content.strip().upper()

    except Exception as e:
        print("CLASSIFIER ERROR:", str(e))
        return "AGRI"  # safe fallback


# Main AI function
def ask_ai(query, phone, name=None):
    system_msg = SYSTEM_PROMPT
    if name:
        system_msg += f"\nThe user's name is {name}. Use it naturally where appropriate. "
        
    query = query.lower()

    try:
        # Get conversation history from DB
        history = get_recent_messages(phone)

        # Classify intent
        classification = classify_query(query)

        # Block unrelated queries
        if classification == "OTHER":
            return "🌱 I focus on farming advice. Ask me about crops, livestock, or farm management."

        # Build conversation context
        messages = [
            {"role": "system", "content": system_msg}
        ] + history + [
            {"role": "user", "content": query}
        ]

        # Generate response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content

        # Clean formatting for WhatsApp
        reply = reply.replace("#", "").replace("*", "").strip()

        # Save conversation
        save_message(phone, "user", query)
        save_message(phone, "assistant", reply)

        return reply

    except Exception as e:
        print("AI ERROR:", str(e))
        return "⚠️ I’m having trouble right now. Please try again shortly."