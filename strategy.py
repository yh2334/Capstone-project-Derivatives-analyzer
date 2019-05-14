import numpy as np
import pandas as pd

columns = ['ask', 'bid', 'contractSymbol','impliedVolatility', 'strike', 'days to expiration', 'Spot Price', 'Call_Put_Flag', 'Long_Short_Flag']


class StrategyManager():
    def __init__(self):
        self.df = pd.DataFrame(columns = columns)
        self.i = 0

    def add_option(self, query):
        self.df.loc[self.i] = query
        self.i = self.i + 1

    def get_options(self):
        options = self.df
        return options

    def clear_options(self):
        self.i = 0
        self.df = pd.DataFrame(columns = columns)


stmanager = StrategyManager()
query = [0, 0, 'AAPL', 0 ,0, 0, 0, 'Call', 0]
stmanager.add_option(query)