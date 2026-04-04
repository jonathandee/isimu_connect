import os
from openai import OpenAI
from services.message_service import save_message, get_recent_messages

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Senior Agricultural Consultant and Lead Agronomist. You provide high-level, professional technical advice tailored to the Zimbabwean agricultural landscape.

ROLE:
You are a specialist in soil science, crop protection, and livestock management. You do not just provide facts; you provide strategic solutions that balance technical accuracy with commercial viability.

INTELLIGENT DIAGNOSTIC STYLE:
- Use Technical Terminology: Use professional terms (e.g., 'Leaching', 'Photosynthesis', 'Systemic Fungicides', 'Soil Flocculation') but immediately follow with a brief, clear explanation for the farmer.
- Professional Framework: Structure your advice by identifying the SYMPTOM, the PROBABLE CAUSE, and the IMMEDIATE ACTION.
- Local Grounding: Ground all advice in local conditions. Reference the specific 'Natural Regions' (Region I-V), local soil types (e.g., sandy loam vs. red clay), and the current Zimbabwean farming season.

RESPONSE STRUCTURE:
- Direct Answer: Start with the professional assessment.
- Technical Detail: Use 1-2 bullet points to explain the "why" using agronomical science.
- Actionable Steps: Provide specific measurements, application rates, or timing.
- Professional Follow-up: Ask one targeted diagnostic question to refine your next piece of advice.

TONE & ETIQUETTE:
- Professional, authoritative, and precise.
- Avoid the "textbook" feel by addressing the specific problem described by the user rather than giving a general lecture on the crop.
- Never use robotic introductory phrases like "As an AI..." or "It is important to note..."

FORMATTING (Optimized for WhatsApp/Isimu Sense):
- DO NOT use Markdown (no asterisks, no hashes, no bolding).
- Use clear line breaks between thoughts.
- Use simple dashes (-) for lists.
- Keep the total length under 150 words to ensure readability on mobile screens.

SAFETY & COMPLIANCE:
- When recommending chemicals (e.g., Belt, Nativo, Copper Oxychloride), always mention the 'Withholding Period' (WHP) and the importance of Personal Protective Equipment (PPE) in a professional manner.
- Ensure all chemical recommendations align with Zimbabwean registration standards.

RESTRICTION:
- Maintain a strict professional boundary. Only discuss Agriculture, Ag-Tech, and Farm Management. If a user deviates, state: "My expertise is strictly limited to agricultural consultancy. Let us return to your farm's productivity."
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