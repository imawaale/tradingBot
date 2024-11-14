"""the file that contains the dbmanager class"""

import json


class DBManager:
    """the class that manages the database"""

    def __init__(self, db_path: str) -> None:
        """initializes the dbmanager class

        Args:
            db_path (str): path to the data json file
        """
        self.db_path = db_path

    def store_info(self, info: dict) -> None:
        """stores info for certain stocks

        Args:
            info (dict): the info on the stock
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)

        symbol = info["Symbol"]
        price = info["price"]
        volume = info["volume"]

        try:
            data[symbol]["info"] = {"price": price, "volume": volume}
        except KeyError:
            data[symbol] = {"info": {"price": price, "volume": volume}}

        with open(self.db_path, "w") as file:
            json.dump(data, file)

    def store_trade(self, trade: dict) -> None:
        """stores a trade in the database

        Args:
            trade (dict): the trade to store
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)

        symbol = trade["Symbol"]
        amount = trade["Amount"]
        price = trade["Price"]
        trade_time = trade["Time"]
        trade_type = trade["Type"]
        trade_data = {"price": price, "amount": amount, "type": trade_type}
        try:
            data[symbol]["trades"][trade_time] = trade_data
        except KeyError:
            data[symbol]["trades"] = {trade_time: trade_data}

        with open(self.db_path, "w") as file:
            json.dump(data, file)

    def get_trades(self, stock: str) -> dict:
        """gets the trades of a user

        Args:
            stock (str): the stock symbol

        Returns:
            dict: the trades of the user for that stock
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)

        try:
            return data[stock]["trades"]
        except KeyError:
            return dict()

    def store_sl(self, stock: str, price: float, percentage: int) -> None:
        """stores a stop loss in the database

        Args:
            stock (str): the stock to set the stop loss for
            price (float): the price to set the stop loss at
            percentage (int): the percentage to set the stop loss at
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)

        try:
            data[stock]["sell-at"][str(price)] = percentage
        except KeyError:
            data[stock]["sell-at"] = {str(price): percentage}

        with open(self.db_path, "w") as file:
            json.dump(data, file)

    def remove_sl(self, stock: str, price: float) -> None:
        """removes a stop loss from the database
        Args:
            stock (str): the stock to remove the stop loss from
            price (float): the price to remove the stop loss at
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)

        del data[stock]["sell-at"][str(price)]

        with open(self.db_path, "w") as file:
            json.dump(data, file)

    def get_sl(self, stock: str) -> dict:
        """gets the stop loss for a stock
        Args:
            stock (str): the stock to get the stop loss for

        Returns:
            dict: the stop loss for the stock
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)

        try:
            return data[stock]["sell-at"]
        except KeyError:
            return dict()

    def get_perc_incr(self, stock: str, timeFrame: str) -> float:
        """gets percentage increase of stock

        Args:
            stock (str): the stock symbol
            timeFrame (str): time frame as : 24H, 7D, 30D

        Returns:
            float : returns the percenatge increase of stock
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)

        return data[stock]["info"]["perc increase"][timeFrame]

    def update_perc_incr(self, stock: str, percenatge: float, timeFrame: str) -> None:
        """updates percentage increase

        Args:
            stock (str): stock symbol
            percenatge (float): updated percentage
            timeFrame (str): time frame as : 24H, 7D, 30D
        """
        with open(self.db_path, "r") as file:
            data = json.load(file)
        try:
            data[stock]["info"]["perc increase"][timeFrame] = percenatge
        except KeyError:
            data[stock]["info"]["perc increase"] = {timeFrame: percenatge}

        with open(self.db_path, "w") as file:
            json.dump(data, file)
