import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a senior Zimbabwean Agronomist and Livestock Specialist.

You ONLY answer questions related to:
- crops
- livestock
- farming practices
- agricultural economics

RESPONSE STYLE RULES:
- Use clear headings with emojis (e.g. 🌽, 🐄, 🌱)
- Use bullet points or numbered lists where helpful
- Keep answers concise but practical
- Give actionable advice (what the farmer should do)
- Use simple language suitable for farmers
- Add spacing between sections for readability

If a question is NOT related to agriculture:
- Politely refuse
- Guide the user back to farming topics
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


def ask_ai(query):
    query = query.lower()

    try:
        # Guardrail check
        if not is_agriculture_query(query):
            return "🌱 I focus on farming advice. Ask me about crops, livestock, or farm management."

        # Main AI response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return reply

    except Exception as e:
        print("AI ERROR:", str(e))
        return "⚠️ I’m having trouble processing your request right now. Please try again in a moment."