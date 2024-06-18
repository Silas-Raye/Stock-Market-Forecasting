import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide

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
            
            print('Buy order sent')
        except Exception as e:
            print(f"Failed to place buy order for {symbol}: {e}")

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
            
            print('Sell order sent')
        except Exception as e:
            print(f"Failed to place sell order for {symbol}: {e}")

    def schedule_sell(self, symbol, qty):
        # Schedule to sell all shares of the stock one week after buying
        def sell_job():
            self.sell(symbol, qty)
        
        sell_time = datetime.now() + timedelta(weeks=1)
        delay = (sell_time - datetime.now()).total_seconds()
        threading.Timer(delay, sell_job).start()
        print(f"Scheduled to sell all shares of {symbol} on {sell_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def prtin_pos(self):
        for position in self.positions:
            print("{} shares of {}".format(position.qty, position.symbol))

alpaca_trade = Alpaca_Trade()

print(alpaca_trade.get_cash_assets())
