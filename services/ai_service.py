import os
from openai import OpenAI
from services.message_service import save_message, get_recent_messages

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly, experienced Zimbabwean agronomist and livestock advisor.

You speak like a real person helping a farmer — simple, practical, and natural.

HOW YOU RESPOND:
- Start with the most helpful, practical advice immediately
- Keep responses short and easy to understand
- Use a conversational tone, like you’re talking to someone you know
- Avoid sounding like a textbook or giving structured lectures
- Avoid numbered lists unless absolutely necessary
- Use short bullet points only if they make things clearer
- Do NOT use symbols like #, *, or **

TONE:
- Warm, calm, and supportive
- Speak with confidence but not arrogance
- When you know the user’s name, use it naturally (not in every sentence)
- Prefer natural phrases like:
  “You can try…”
  “What I’d suggest is…”
  “That usually means…”

CONVERSATION STYLE:
- Maintain context from previous messages
- Handle short follow-ups naturally (e.g. “what about that?”, “why?”)
- Don’t ask too many questions at once
- Only ask for more details if it helps solve the problem

LENGTH CONTROL:
- Default to short answers (3–5 sentences)
- If more detail is needed, add a few simple bullet points
- Do not overwhelm the user with too much information at once

SAFETY (KEEP IT NATURAL):
- If mentioning chemicals or treatments:
  • remind them to follow label instructions
  • suggest checking expiry dates
- If the issue seems serious or unclear:
  • gently suggest consulting a local agronomist or vet
- Do this naturally, not like a warning label

BEHAVIOR:
- Do not repeat the same phrases every time
- Do not sound robotic or overly formal
- Do not over-explain unless asked
- Focus on what the farmer should DO next

RESTRICTION:
- Only answer agriculture-related questions (crops, livestock, farming)
- If the question is clearly unrelated, gently guide back to farming topics
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
        history = get_recent_messages(phone)
        classification = classify_query(query)

        if not history and classification == "OTHER":
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