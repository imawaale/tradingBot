import os
import alpaca_trade_api
import time
from Exceptions import InsuffecientFunds
from datetime import datetime, timedelta
from dotenv import load_dotenv
from alpaca_trade_api.rest import APIError

load_dotenv()




class BrokerConn:
    def __init__(
        self, API_KEY, SECRET_KEY, BASE_URL="https://paper-api.alpaca.markets"
    ):
        """
        Initialize the BrokerConn instance with Alpaca API credentials and base URL.

        :param API_KEY: The API key for Alpaca.
        :param SECRET_KEY: The secret API key for Alpaca.
        :param BASE_URL: The base URL for Alpaca API (default is for paper trading).
        """
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.BASE_URL = BASE_URL
        self.api = alpaca_trade_api.REST(
            API_KEY, SECRET_KEY, BASE_URL, api_version="v2"
        )

    def create_trade(self, Stock: str, Amount: float) -> dict:
        """
        Create a trade to buy a specified amount of stock.

        :param Stock: The stock symbol to buy.
        :param Amount: The amount (number of shares) of the stock to buy.
        :raises ValueError: If the stock symbol is not found.
        :raises InsuffecientFunds: If the balance is less than the estimated cost of the trade.
        :return: A dictionary containing trade details:
                 - "Amount": Amount of the stock purchased.
                 - "Price": Price of the stock at the time of purchase.
                 - "Time": Time when the trade was completed (UTC).
                 - "Type": failed or successful trade.
        """
        estimatedCost = self.api.get_latest_trade(Stock).price * Amount
        if estimatedCost > self.get_balance():
            raise InsuffecientFunds(self.get_balance(), estimatedCost)

        order = self.api.submit_order(
            symbol=Stock,
            qty=Amount,
            side="buy",
            type="market",
            time_in_force="ioc",  # immediate or cancelled
        )

        while True:
            filledOrder = self.api.get_order(order.id)
            if filledOrder.status == "filled":
                tradeData = {
                    "Symbol": Stock,
                    "Amount": Amount,
                    "Price": float(filledOrder.filled_avg_price),
                    "Time": datetime.utcnow().strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),  # current UTC time
                    "Type": "buy",
                }
                break
            elif filledOrder.status == "canceled":
                tradeData = {
                    "Symbol": Stock,
                    "Amount": Amount,
                    "Price": float(self.api.get_latest_trade(Stock).price),
                    "Time": datetime.utcnow().strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),  # current UTC time
                    "Type": "failed_buy",
                }
                break
            time.sleep(1)  # Wait for a second before checking again

        return tradeData

    def leave_trade(self, Stock: str, Amount: float) -> dict:
        """
        Sell a specified amount of stock from the portfolio.

        :param Stock: The stock symbol to sell.
        :param Amount: The amount (number of shares) of the stock to sell.
        :raises ValueError: If the stock is not found in the portfolio or if there are not enough shares to sell.
        :return: A dictionary containing trade details:
                 - "Cash": Amount of money received from the sale.
                 - "Price": Price of the stock at the time of sale.
                 - "Time": Time when the trade was completed (UTC).
                 - "Type": failed or successful trade.
        """
        # Check if the stock is in the portfolio
        try:
            position = self.api.get_position(Stock)
        except APIError:
            raise ValueError("Stock not in portfolio")
        # If the amount to sell is more than available, raise ValueError
        if int(position.qty) < Amount:
            raise ValueError(
                f"Not enough shares of {Stock} to sell. Available: {position.qty}, Requested: {Amount}"
            )

        # Place a market order to sell the stock
        order = self.api.submit_order(
            symbol=Stock, qty=Amount, side="sell", type="market", time_in_force="ioc"
        )

        # Wait for the order to be filled
        while True:
            newOrder = self.api.get_order(order.id)
            if newOrder.status == "filled":
                tradeData = {
                    "Symbol": Stock,
                    "Cash": float(newOrder.filled_avg_price) * Amount,
                    "Price": float(newOrder.filled_avg_price),
                    "Time": datetime.utcnow().strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),  # Use the current UTC time
                    "Type": "sell",
                }
                break
            elif newOrder.status == "canceled":
                tradeData = {
                    "Symbol": Stock,
                    "Cash": float(self.api.get_latest_trade(Stock).price) * Amount,
                    "Price": float(self.api.get_latest_trade(Stock).price),
                    "Time": datetime.utcnow().strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),  # Use the current UTC time
                    "Type": "failed_sell",
                }
                break
            time.sleep(1)  # Wait for a second before checking again

        return tradeData

    def get_info(self, Stock: str, time=None) -> dict:
        """
        Get information about a stock at a specific time.

        :param Stock: The stock symbol to retrieve information for.
        :param time: The time to get the information for. Defaults to current time.
        :raises ValueError: If no data is available for the stock symbol.
        :return: A dictionary containing stock information:
                 - "Price": The closing price of the stock.
                 - "Volume": The volume of trades.
                 - "Time": The time of the bar data (UTC).
        """
        # Default time to current time if not provided
        if time is not None:
            time = datetime.fromisoformat(time.replace("Z", "+00:00"))
            # Format time to string RFC3391 format
            startTime = (time - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            endTime = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            # Fetch bar data for the stock symbol
            barset = self.api.get_bars(Stock, "1min", startTime, endTime)
            # Check if symbol exists in the response
            if not barset:
                raise ValueError(f"No data available for stock symbol '{Stock}'")

            # Get the most recent bar data
            bar = barset[0]

            return {
                "Symbol": Stock,
                "Price": bar.c,  # Close price of the stock
                "Volume": bar.v,  # Volume of trades
                "Time": bar.t.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Time of the bar data
            }

        return {
            "Symbol": Stock,
            "Price": self.api.get_latest_trade(Stock).price,
            "Volume": self.api.get_latest_trade(Stock).size,
            "Time": self.api.get_latest_trade(Stock).timestamp.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        }

    def get_balance(self) -> float:
        return float(self.api.get_account().cash)


trader = BrokerConn(
    API_KEY=os.getenv("API_KEY"),
    SECRET_KEY=os.getenv("SECRET_ALPACA_KEY"),
    BASE_URL=os.getenv("BASE_URL")  
)


# Example usage
print(trader.get_balance())
print(trader.leave_trade("AAPL", 2))
print(trader.get_info("AAPL"))
print(trader.get_info("TSLA"))



