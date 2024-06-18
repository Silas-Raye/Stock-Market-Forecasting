import yfinance as yf
from datetime import datetime, timedelta
import threading
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil

def print_with_date(message):
  now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(f"{now}: {message}")

class Alpaca_Trade():
    def __init__(self):
        # get alpaca api keys
        with open('alpaca_api_keys.txt', 'r') as file:
            api_keys = file.readlines()

        live_api_key = api_keys[0].strip()
        live_api_secret = api_keys[1].strip()
        paper_api_key = api_keys[2].strip()
        paper_api_secret = api_keys[3].strip()

        # setup trading client, account, and positions vars
        self.trading_client = TradingClient(paper_api_key, paper_api_secret, paper=True)
        self.account = self.trading_client.get_account()
        self.positions = self.trading_client.get_all_positions()

    def get_cash_assets(self):
        return float(self.account.cash)

    def buy(self, symbol, qty):
        try:
            # setting parameters for our buy order
            market_order_data = MarketOrderRequest(symbol=symbol, qty=qty, side = OrderSide.BUY, time_in_force = 'day')

            # submitting the order and then saving the returned object to a text file
            market_order = self.trading_client.submit_order(market_order_data)
            with open('market_orders.txt', 'a') as f:
                f.write('NEW ORDER:\n')
                for property_name, value in market_order:
                    f.write(f'"{property_name}": {value}\n')
            
            print_with_date('Buy order sent')
        except Exception as e:
            print_with_date(f"Failed to place buy order for {symbol}: {e}")

    def sell(self, symbol, qty):
        try:
            # setting parameters for our sell order
            market_order_data = MarketOrderRequest(symbol=symbol, qty=qty, side = OrderSide.SELL, time_in_force = 'day')

            # submitting the order and then saving the returned object to a text file
            market_order = self.trading_client.submit_order(market_order_data)
            with open('market_orders.txt', 'a') as f:
                f.write('NEW ORDER:\n')
                for property_name, value in market_order:
                    f.write(f'"{property_name}": {value}\n')
            
            print_with_date('Sell order sent')
        except Exception as e:
            print_with_date(f"Failed to place sell order for {symbol}: {e}")

    def schedule_sell(self, symbol, qty):
        # Schedule to sell all shares of the stock one week after buying
        def sell_job():
            self.sell(symbol, qty)
        
        sell_time = datetime.now() + timedelta(weeks=1)
        delay = (sell_time - datetime.now()).total_seconds()
        threading.Timer(delay, sell_job).start()
        print_with_date(f"Scheduled to sell all shares of {symbol} on {sell_time.strftime('%Y-%m-%d %H:%M:%S')}")

alpaca_trade = Alpaca_Trade()

def scrape_csv():
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

        # Cleaning and converting price column
        insider_trades_df['Price'] = insider_trades_df['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)

        # Rename 'Trade\xa0Date' to 'Trade Date' and do the same for other cols
        insider_trades_df.rename(columns={'Trade\xa0Date': 'Trade Date'}, inplace=True)
        insider_trades_df.rename(columns={'Filing\xa0Date': 'Filing Date'}, inplace=True)
        insider_trades_df.rename(columns={'Company\xa0Name': 'Company Name'}, inplace=True)
        insider_trades_df.rename(columns={'Trade\xa0Type': 'Trade Type'}, inplace=True)

        # Convert 'Trade Date' to datetime
        insider_trades_df['Trade Date'] = pd.to_datetime(insider_trades_df['Trade Date'])

        # Sort the DataFrame by 'Trade Date'
        insider_trades_df.sort_values(by='Trade Date', inplace=True)

        # Set the display option to show all rows
        pd.set_option('display.max_rows', None)

        # Output the results to a new CSV file
        output_file_path = 'cluster_buys.csv'  # Replace with your desired output file path
        insider_trades_df.to_csv(output_file_path, index=False)

        # Return the DataFrame for further processing
        return insider_trades_df
    else:
        print_with_date("Table not found on the page")
        return None

def compare_csvs(new_csv='cluster_buys.csv', old_csv='old_cluster_buys.csv'):
    if not os.path.exists(old_csv):
        print_with_date("No previous CSV to compare with")
        return
    
    new_df = pd.read_csv(new_csv)
    old_df = pd.read_csv(old_csv)
    
    # Finding new entries
    new_entries = pd.concat([new_df, old_df]).drop_duplicates(keep=False)
    
    if not new_entries.empty:
        print_with_date("New entries found")
        tickers = new_entries['Ticker'].tolist()
        return tickers
    else:
        print_with_date("No new entries found")
        return []
    
def max_shares_under_500(ticker):
    try:
        # Get the current stock information
        stock = yf.Ticker(ticker)
        current_price = stock.history(period="1d")['Close'].iloc[0]
        
        # Calculate the maximum number of shares
        max_shares = int(500 / current_price)
        
        return max_shares
    except Exception as e:
        print_with_date(f"Error: {e}")
        return 0

# Run the scraping function
scrape_csv()

# Compare the new CSV with the previous one
tickers = compare_csvs()

if tickers is not None:
    for ticker in tickers:
        if alpaca_trade.get_cash_assets() >= 1100:
            print_with_date("Buying " + ticker)
            qty = max_shares_under_500(ticker)
            alpaca_trade.buy(ticker, qty)
            #alpaca_trade.schedule_sell(ticker, qty)

# Backup the new CSV for the next comparison
if os.path.exists('cluster_buys.csv'):
    shutil.copy('cluster_buys.csv', 'old_cluster_buys.csv')
