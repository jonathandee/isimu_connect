SYSTEM_PROMPT = """
You are a senior Zimbabwean Agronomist and Data Analyst.
"""

def ask_ai(query):
    query = query.lower()

    # Basic smart mock logic (feels real, not fake)
    if "maize" in query and "yellow" in query:
        return """
🌽 AI Agronomist Advice:

Your maize leaves turning yellow is likely due to **Nitrogen deficiency**.

✅ What to do:
- Apply Ammonium Nitrate (AN) or Urea
- Ensure adequate soil moisture
- Check for waterlogging

📍 Local Tip:
In Zimbabwe, this is common during early vegetative stage.

⚠️ Always follow fertilizer instructions and wear PPE.
"""

    elif "tomato" in query:
        return """
🍅 AI Agronomist Advice:

Possible issue: pest attack (e.g. Tuta absoluta) or nutrient imbalance.

✅ What to do:
- Inspect underside of leaves
- Use recommended pesticide
- Maintain proper spacing and airflow

⚠️ Follow chemical label instructions and use PPE.
"""

    else:
        return f"""
🌱 AI Agronomist (Mock Mode):

For your query: {query}

- Conduct soil analysis
- Monitor irrigation
- Check for pests and diseases

⚠️ Always follow chemical label instructions and use PPE.
"""