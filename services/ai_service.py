import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a senior Zimbabwean Agronomist and Data Analyst.
Give practical, local farming advice.
"""

def ask_ai(query):
    query = query.lower()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("AI ERROR:", str(e))

        # fallback (your smart logic)
        if "maize" in query and "yellow" in query:
            return "Maize yellow leaves likely nitrogen deficiency. Apply AN or Urea."

        elif "tomato" in query:
            return "Possible pest issue like Tuta absoluta. Inspect leaves and spray accordingly."

        return f"Fallback advice: Check soil, water, and pests."