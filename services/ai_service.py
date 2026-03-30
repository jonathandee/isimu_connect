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
- If the user asks a follow-up, continue naturally without restarting

CONTENT:
- Focus on what the farmer should DO
- Only explain deeper details if necessary

RESTRICTION:
- Only answer agriculture-related questions
- If not related, guide the user back to farming topics
"""

# Guardrail: classify query
def is_agriculture_query(query):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Answer ONLY with YES or NO."},
                {"role": "user", "content": f"Is this question related to agriculture: {query}"}
            ]
        )

        answer = response.choices[0].message.content.lower()
        return "yes" in answer

    except Exception as e:
        print("CLASSIFIER ERROR:", str(e))
        return True  # fallback: allow instead of blocking


def ask_ai(query, phone):
    query = query.lower()

    try:
        if not is_agriculture_query(query):
            return "🌱 I focus on farming advice. Ask me about crops, livestock, or farm management."

        # Get conversation history from DB
        history = get_recent_messages(phone)

        # Add new user message
        history.append({"role": "user", "content": query})

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + history

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content
        reply = reply.replace("#", "").replace("*", "")

        # Save both messages
        save_message(phone, "user", query)
        save_message(phone, "assistant", reply)

        return reply.strip()

    except Exception as e:
        print("AI ERROR:", str(e))
        return "⚠️ I’m having trouble right now. Please try again shortly."