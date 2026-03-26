from db import get_connection

def get_price(item):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT price, location 
        FROM market_prices 
        WHERE commodity = %s 
        ORDER BY timestamp DESC 
        LIMIT 1
    """

    cur.execute(query, (item,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        price, location = result
        return f"{item.capitalize()} is ${price}/kg at {location}."
    
    return "Price not available."