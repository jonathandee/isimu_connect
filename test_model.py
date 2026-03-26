from google import genai

client = genai.Client(api_key="AIzaSyBAufADpBhHO5sqxywnHcP-k3ZJXeUZPJg")

models = client.models.list()

for m in models:
    print(m.name)
    
    