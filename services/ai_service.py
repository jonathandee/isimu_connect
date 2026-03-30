import os
from openai import OpenAI
from services.message_service import save_message, get_recent_messages

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly and experienced Zimbabwean agronomist.

You speak like a real person helping a farmer — not like a textbook or lecture.

STYLE:
- Be conversational and natural
- Start with the direct answer, not explanations
- Avoid numbered lists unless absolutely necessary
- Avoid formal headings like "Mode of Action"
- Use simple sentences
- Use bullet points only when it makes things clearer
- DO NOT use markdown symbols like #, *, or **

TONE:
- Sound practical, calm, and helpful
- Give advice like you’re talking to a fellow farmer
- Keep it short unless more detail is really needed

CONTEXT:
- Maintain conversation context
- Handle follow-up questions naturally

CONTENT:
- Focus on what the farmer should DO
- Only explain deeper details if necessary

RESTRICTION:
- Only answer agriculture-related questions
- If not related, guide the user back to farming topics
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
def ask_ai(query, phone):
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
            {"role": "system", "content": SYSTEM_PROMPT}
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