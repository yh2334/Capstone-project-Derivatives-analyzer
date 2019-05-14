import pandas as pd
import numpy as np
import json
from urllib.request import urlopen
from scipy.stats import norm


def optionsdata(ticker):
    site = 'https://query2.finance.yahoo.com/v7/finance/options/' + ticker
    with urlopen(site) as response:
        DATA = response.read().decode()
        DATA = json.loads(DATA)

    Expirations = DATA["optionChain"]['result'][0]['expirationDates']
    Expiration_Dates = pd.to_datetime(Expirations, unit='s')
    Strikes = pd.Series(DATA["optionChain"]['result'][0]['strikes'])
    strikes = DATA["optionChain"]['result'][0]['strikes']
    ###collecting stock data####
    index = []
    entry = []
    for a in DATA["optionChain"]['result'][0]['quote'].items():
        index.append(a[0])
        entry.append(a[1])

    todays_quotes = pd.DataFrame(entry, index=index, columns=['Entry'])
    Master_List = []
    Master_Calls = []
    Master_Puts = []
    for expiration in Expirations:
        try:

            expiry = str(expiration)
            expiration_date = pd.to_datetime(expiration, unit='s')
            new_site = 'https://query2.finance.yahoo.com/v7/finance/options/' + ticker + '?date=' + expiry

            with urlopen(new_site) as response:
                DATA = response.read().decode()
                DATA = json.loads(DATA)
                Master_List.append(DATA)
                Call_df = pd.read_json(json.dumps(DATA['optionChain']['result'][0]['options'][0]['calls']))
                Put_df = pd.read_json(json.dumps(DATA['optionChain']['result'][0]['options'][0]['puts']))
                Master_Calls.append(Call_df)
                Master_Puts.append(Put_df)
        except:
            Exception

    Calls = pd.concat(Master_Calls, sort=True)
    Puts = pd.concat(Master_Puts, sort=True)
    spot = todays_quotes.loc['regularMarketPrice'].iloc[0]

    # Clean Call Data
    Calls = clean_options_df(Calls, spot, 'Call')
    Puts = clean_options_df(Puts, spot, 'Put')

    data = pd.concat([Calls, Puts], axis=0)
    data = data.reset_index()
    return data


def per_dollar_basis(df):
    delta = df['delta']
    gamma = df['gamma']
    try:
        price = df['lastPrice']
    except:
        price = df['Ask']
    try:
        dol_per_delta = price / delta
        dol_per_gamma = price / gamma
    except:
        dol_per_delta = np.nan
        dol_per_gamma = np.nan

    return pd.Series([dol_per_delta, dol_per_gamma])


def clean_options_df(df, spot_price, call_put_flag):
    df = df.drop(['contractSize', 'currency'], axis=1)
    df['expiration'] = pd.to_datetime(df['expiration'], unit='s')
    today = pd.to_datetime(pd.Timestamp.today().strftime('%D'))
    df['days to expiration'] = (df['expiration'] - today).dt.days
    df['B/A Spread'] = df['ask'] - df['bid']

    df = df.dropna()
    df = df.reset_index()
    df = df.drop('index', axis=1)
    df['lastTradeDate'] = pd.to_datetime(df['lastTradeDate'], unit='s')
    df['Days Since Last Trade'] = -(df['lastTradeDate'] - today).dt.days
    df['Spot Price'] = spot_price
    df['Call_Put_Flag'] = call_put_flag
    return df
