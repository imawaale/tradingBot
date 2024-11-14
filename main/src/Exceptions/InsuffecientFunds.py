""" Contains the implemntation for the InsuffecientFunds exception"""
class InsuffecientFunds(ValueError):
    """ Raised when the user tries to buy more than they have
    Attributes:
        available_funds: The amount of funds the user has
        amount_needed: The amount the user is trying to buy
    """
    def __init__(self, availableFunds: float, amountToBuy: float):
        """Initializes the InsuffecientFunds exception

        Args:
            availableFunds (float): Amount of funds the user has
            amountToBuy (float): Amount the user is trying to buy

        Raises:
            ValueError: If the user has enough funds so the exception should not be raised
        """
        if availableFunds >= amountToBuy:
            raise ValueError("Insuffecient funds should not be raised if the user has enough funds?")
        self.available_funds = availableFunds
        self.amount_needed = amountToBuy
        self.missing_funds = amountToBuy - availableFunds

    def __str__(self):
        return f"Missing £{self.missing_funds}"
