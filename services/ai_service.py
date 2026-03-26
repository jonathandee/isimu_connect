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
        return f"AI error: {str(e)}"

    # fallback logic (your maize/tomato rules)