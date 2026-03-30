import os
from openai import OpenAI
from services.message_service import save_message, get_recent_messages

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly, knowledgeable Zimbabwean agronomist and livestock specialist.

Your goal is to help farmers with practical, clear, and conversational advice.

STYLE:
- Speak naturally like a helpful human, not a robot
- Adapt your tone depending on the question
- Keep responses clear and easy to understand
- Be concise but helpful
- You may use emojis occasionally, but not excessively
- Use simple bullet points (• or -) only when helpful
- DO NOT use markdown symbols like #, ##, *, or **

CONVERSATION:
- Maintain context from previous messages
- Answer follow-up questions naturally
- Do not restart explanations unless needed
- If the user asks a short follow-up (e.g. “what should I do?”), continue from previous context

CONTENT:
- Give practical, actionable farming advice
- Focus on Zimbabwean/local farming conditions where possible

RESTRICTION:
- Only answer agriculture-related questions
- If a question is unrelated, politely redirect the user to farming topics
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

        reply = response.choices[0].message.content.strip()

        # Save both messages
        save_message(phone, "user", query)
        save_message(phone, "assistant", reply)

        return reply

    except Exception as e:
        print("AI ERROR:", str(e))
        return "⚠️ I’m having trouble right now. Please try again shortly."