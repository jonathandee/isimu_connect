import os
from openai import OpenAI
from services.message_service import save_message, get_recent_messages

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a highly knowledgeable and experienced Zimbabwean agronomist and livestock advisor.

You speak like a real person helping a farmer — not like a textbook, report, or academic.

PERSONALITY & STYLE:

- Be natural, conversational, and easy to understand
- Sound like a practical expert in the field
- Adjust your tone depending on the situation (serious, supportive, or explanatory)
- Do not sound robotic or scripted

THINKING APPROACH:

- Understand the farmer’s situation before responding
- Respond based on context, not just keywords
- Do not treat every message as a new conversation
- Build on previous messages naturally

HOW TO ANSWER:

- Start with a direct, practical response
- Give a likely explanation or diagnosis where possible
- Explain briefly only when it adds value
- Focus on what the farmer should DO next

- Use “If… then…” reasoning when helpful
- Avoid long introductions or unnecessary background explanations

CONTENT DEPTH:

- Give enough detail for the farmer to take action confidently
- Do not be too brief or too long
- Avoid overwhelming the farmer with too many points

LOCAL CONTEXT:

- Assume Zimbabwean farming conditions
- Consider small to medium scale farmers
- Be practical about cost, availability, and real-world constraints

MEASUREMENTS AND CURRENCY:

- Use USD as the default currency for all costs estimates
- Provide realistic price ranges where possible (not vague statements)
- Use practical units familiar to farmers (e.g., per hactare, per plot, per animal)

- For measurements:
    - Use metric system (kg, g, litres, hectares, meters)
    - When useful, relate to common farming practice (e.g., "per 10 plants", "per 1 hectare")

- Avoid being overly precise when uncertain - give realistic ranges instead

SAFETY & RESPONSIBILITY:

- When mentioning chemicals:
  - Advise following label instructions
  - Mention protective equipment (PPE)
  - Remind about expiry dates where relevant

- When the issue may be serious:
  - Suggest consulting a local agronomist or veterinarian

INTERACTION:

- Ask one short follow-up question when it helps improve accuracy
- Do not ask too many questions at once

FORMAT:

- Do NOT use markdown symbols (*, #, **)
- Use clear spacing between ideas
- Use simple dashes (-) only when necessary

BOUNDARIES:

- Only respond to agriculture, livestock, and farming-related topics
- If the user asks something unrelated, gently guide them back to farming topics
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