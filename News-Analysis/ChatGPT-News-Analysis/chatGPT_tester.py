import config
import openai

openai.api_key = config.GPT_KEY

name = "Microsoft"
headline = "Microsoft stock to do something"
prompt = f"Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. Answer “YES” if good news, “NO” if bad news, or “UNKNOWN” if uncertain. Is this headline good or bad for the stock price of company {name} in the short term? Headline: {headline}"

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "user",
      "content": prompt
    }
  ],
  temperature=1,
  max_tokens=2
)

# Extract and print the model's generated text
reply = response["choices"][0]["message"]["content"]

def map_response(reply):
    return {
        "YES": 1,
        "NO": -1,
        "UNKNOWN": 0
    }.get(reply, None)

result = map_response(reply)

print(result)