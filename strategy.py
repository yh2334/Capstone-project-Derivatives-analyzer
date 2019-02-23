import pandas as pd
import math
import numpy as np


class sfManager( object ):
    def __init__(self, df):
        self.df = df

    def add_option(self, query_result):
        self.df.append(self, query_result)

    def get_option(self):
        return self.df

    def clear(self):
        self.df = pd.DataFrame(index=[])


