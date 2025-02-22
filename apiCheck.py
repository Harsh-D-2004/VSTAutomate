import openai

# Replace with your actual API key
client = openai.OpenAI(api_key="")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("API Key is working!")
    print("Response:", response.choices[0].message.content)
except openai.AuthenticationError:
    print("Invalid API Key!")
except Exception as e:
    print(f"An error occurred: {e}")
