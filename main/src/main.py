import os
from dotenv import load_dotenv
from BrokerConn import BrokerConn
from ML_model import run_trading_bot

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys and base URL from environment variables
API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_ALPACA_KEY")
BASE_URL = os.getenv("BASE_URL")

# Initialize Broker Connection
trader = BrokerConn(API_KEY, SECRET_API_KEY, BASE_URL)

def main():
    # Example stock symbol to trade
    ticker = "TSLA"  # You can change this to any stock you want to trade
    shares_to_buy = 2  # Number of shares to buy

    # Run the trading bot to get predictions
    run_trading_bot(ticker)

    # Example of creating a trade (paper trade)
    try:
        trade_info = trader.create_trade(ticker, shares_to_buy)
        print("Trade Info:", trade_info)
    except Exception as e:
        print("An error occurred while placing a trade:", str(e))

    # Additional trading logic or backtesting can be added here

if __name__ == "__main__":
    main()
