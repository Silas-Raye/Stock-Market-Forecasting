import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from datetime import datetime

# URL to scrape
url = "http://openinsider.com/latest-cluster-buys"

# Fetch the web page
response = requests.get(url)
html = response.content

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Find the table by its class
table = soup.find('table', {'class': 'tinytable'})

if table:
    rows = table.findAll('tr')

    data = []  # Create a list to store the table data
    for row in rows:
        csv_row = []
        for cell in row.findAll(['td', 'th']):
            # Get the text content and strip any leading/trailing whitespace
            csv_row.append(cell.get_text(strip=True))
        data.append(csv_row)

    # Create a DataFrame from the table data
    columns = data[0]  # Assuming the first row contains column headers
    insider_trades_df = pd.DataFrame(data[1:], columns=columns)

    print("Data has been loaded into a DataFrame")
else:
    print("Table not found on the page")

# Function to fetch current stock price
def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    return hist['Close'][0] if not hist.empty else None

# Cleaning and converting price column
insider_trades_df['Price'] = insider_trades_df['Price'].str.replace('$', '').str.replace(',', '').astype(float)

# Rename 'Trade\xa0Date' to 'Trade Date' and do the same for other cols
insider_trades_df.rename(columns={'Trade\xa0Date': 'Trade Date'}, inplace=True)
insider_trades_df.rename(columns={'Filing\xa0Date': 'Filing Date'}, inplace=True)
insider_trades_df.rename(columns={'Company\xa0Name': 'Company Name'}, inplace=True)
insider_trades_df.rename(columns={'Trade\xa0Type': 'Trade Type'}, inplace=True)

# Convert 'Trade Date' to datetime
insider_trades_df['Trade Date'] = pd.to_datetime(insider_trades_df['Trade Date'])

# Calculate the current date
current_date = datetime.now()

# Adding a new column for current price, price increase, and days since trade
insider_trades_df['Current Price'] = None
insider_trades_df['Price Increase (%)'] = None
insider_trades_df['Days Since Trade'] = (current_date - insider_trades_df['Trade Date']).dt.days

# Process each row
for index, row in insider_trades_df.iterrows():
    ticker = row['Ticker']
    buy_price = row['Price']
    current_price = get_current_price(ticker)

    if current_price is not None:
        increase_percentage = ((current_price - buy_price) / buy_price) * 100
        insider_trades_df.at[index, 'Current Price'] = current_price
        insider_trades_df.at[index, 'Price Increase (%)'] = increase_percentage

# Sort the DataFrame by 'Trade Date'
insider_trades_df.sort_values(by='Trade Date', inplace=True)

# Set the display option to show all rows
pd.set_option('display.max_rows', None)

# Output the results to a new CSV file
output_file_path = 'cluster_buys.csv'  # Replace with your desired output file path
insider_trades_df.to_csv(output_file_path, index=False)

print(f"Data exported to {output_file_path}")
