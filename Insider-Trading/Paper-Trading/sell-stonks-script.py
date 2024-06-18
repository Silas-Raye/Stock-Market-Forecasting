from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide
import re

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

alpaca_trade = Alpaca_Trade()

# Read the contents of the market_orders.txt file
with open('market_orders.txt', 'r') as file:
    orders = file.read()

# Split orders by "NEW ORDER:"
order_list = orders.split("NEW ORDER:")
order_list = [order.strip() for order in order_list if order.strip()]

# Current date
current_date = datetime.now().date()

# Date format in the file
date_format = "%Y-%m-%d"

# Orders to keep
orders_to_keep = []

# Process each order
for order in order_list:
    # Extract the relevant information using regular expressions
    submitted_at_match = re.search(r'"submitted_at": ([\d-]+) ', order)
    symbol_match = re.search(r'"symbol": (\w+)', order)
    qty_match = re.search(r'"qty": (\d+)', order)
    
    if submitted_at_match and symbol_match and qty_match:
        submitted_at = datetime.strptime(submitted_at_match.group(1), date_format).date()
        symbol = symbol_match.group(1)
        qty = int(qty_match.group(1))
        
        # Check if the order was submitted more than 7 days ago
        if (current_date - submitted_at).days >= 7:
            # Sell the stock
            alpaca_trade.sell(symbol, qty)
        else:
            # Keep this order if it's not older than 7 days
            orders_to_keep.append(order)
    else:
        # If any information is missing, keep the order to avoid data loss
        orders_to_keep.append(order)

# Write the remaining orders back to the file
with open('market_orders.txt', 'w') as file:
    for order in orders_to_keep:
        file.write(f"NEW ORDER:\n{order}\n")
