import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from pyfinviz.quote import Quote
import config
import openai
openai.api_key = config.GPT_KEY

ticker = 'MSFT'
threshold_date_str = '2023-09-25'

# Create a Quote object
quote = Quote(ticker=ticker)

# Get the outer news DataFrame
news_df = quote.outer_news_df

# Create a DataFrame from the news data and drop unnecessary columns
df = pd.DataFrame(news_df)
df = df.drop(columns=['URL', 'From'])

# Convert the 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'], format='mixed')

# Convert the threshold date string to datetime
threshold_date = pd.to_datetime(threshold_date_str)

# Use boolean indexing to keep rows after the threshold date
df = df[df['Date'] >= threshold_date]

def get_company_name(ticker):
    try:
        # Create a Ticker object for the stock
        stock = yf.Ticker(ticker)
        
        # Get the company name
        company_name = stock.info.get("longName", "Company not found")
        
        return company_name
    except Exception as e:
        print("Error: Ticker not found")
        return None

def get_single_sentiment(ticker, headline):
    name = get_company_name(ticker)

    prompt = f"Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. Answer 'YES' if good news, 'NO' if bad news, or 'UNKNOWN' if uncertain. Is this headline good or bad for the stock price of company {name} in the short term? Headline: {headline}"

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
        }.get(reply, 0)

    result = map_response(reply)
    print(f"{result}: {headline}")
    return result

predictions = []
for headline in df['Headline']:
    prediction = get_single_sentiment(ticker, headline)
    predictions.append(prediction)

df['Prediction'] = predictions

df.to_csv('my_data.csv', index=False)

print(df)