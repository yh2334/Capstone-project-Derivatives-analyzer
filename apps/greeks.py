import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from app import app, df_to_table, Graph, update_graph, indicator, marks
from scipy.stats import norm

# calculate the greeks
# ['delta', 'gamma', 'vega', 'theta', 'rho', 'lambdaa','epsilon','vanna','charm','volga','DvegaDtime','veta','color','ultima','speed','zomma']

def greeks(df):
    rate = 0.015
    q = 0
    spot = df['Spot Price']
    strike = df['strike']
    vol = df['impliedVolatility']
    maturity = df['days to expiration']
    Call_Put_Flag = df['Call_Put_Flag']

    """ask, bid, change, contractSymbol, expiration,vol, inTheMoney, lastPrice, lastTradeDate,
    openInterest, percentChange, strike, volume,maturity, BA_Spread, DaysSinceLastTrade,
    spot, Call_Put_Flag = list(column_list)"""
    d1 = (np.log(spot / strike) + (maturity / 365) * (rate - q + (vol ** 2) / 2)) / (vol * np.sqrt(maturity / 365))
    d2 = d1 - vol * np.sqrt(maturity / 365)
    gamma = ((np.exp(-q * maturity / 365) / (spot * vol * np.sqrt(maturity / 365))) * 1 / np.sqrt(2 * np.pi)) * np.exp(
        (-d1 ** 2) / 2)
    vega = (((spot * np.exp(-q * maturity / 365)) * np.sqrt(maturity / 365)) / 100) * 1 / np.sqrt(2 * 3.14159) * np.exp(
        (-d1 ** 2) / 2)
    vanna = np.exp(-q * maturity / 365) * np.sqrt(maturity / 365) * (d2 / vol) * np.exp(-(d1 ** 2) / 2) / (2 * np.pi)

    volga = (spot * (np.exp(q * maturity / 365)) * np.sqrt(maturity / 365) * (np.exp(-(d1 ** 2) / 2) * d1 * d2) / (
        np.sqrt(2 * np.pi)) * vol)
    ultima = - vega / (vol * vol) * (d1 * d2 * (1 - d1 * d2) + d1 * d1 + d2 * d2)
    color = - np.exp(-q * maturity / 365) * 1 / np.sqrt(2 * 3.14159) * np.exp((-d1 ** 2) / 2) * 1 / (
                2 * spot * (maturity / 365) * vol * np.sqrt(maturity / 365)) * (2 * q * (maturity / 365) + 1 + (
                2 * (rate - q) * (maturity / 365) - d2 * vol * np.sqrt(maturity / 365) / (
                    vol * np.sqrt(maturity / 365)) * d1))
    zomma = gamma * ((d1 * d2 - 1) / vol)
    speed = - gamma / spot * (d1 / (vol * np.sqrt(maturity / 365)) + 1)
    veta = - spot * np.exp(-q * maturity / 365) * 1 / np.sqrt(2 * 3.14159) * np.exp((-d1 ** 2) / 2) * np.sqrt(
        maturity / 365) * (
                       q + ((rate - q) * d1) / (vol * np.sqrt(maturity / 365) - (1 + d1 * d2) / (2 * (maturity / 365))))

    if Call_Put_Flag == 'Call':
        try:
            delta = np.exp(-q * maturity / 365) * norm.cdf(d1)
        except:
            delta = np.nan
        try:
            theta = ((1 / (maturity / 365)) * -((spot * vol * np.exp(-q * maturity / 365))) / 2 * np.sqrt(
                maturity / 365)) * (np.exp((-d1 ** 2) / 2)) / np.sqrt(2 * 3.14159) - rate * strike * np.exp(
                -rate * maturity / 365) * norm.cdf(d2) + q * spot * np.exp(rate * maturity / 365) * norm.cdf(d1)
        except:
            theta = np.nan
        try:
            rho = strike * maturity / 365 * np.exp(-rate * maturity / 365) * norm.cdf(d2)
        except:
            rho = np.nan

        try:
            epsilon = -strike * (maturity / 365) * np.exp(-q * maturity / 365) * norm.cdf(d1)
        except:
            epsilon = np.nan

        try:
            part1 = -q * (np.exp(-q * maturity / 365)) * norm.cdf(d1)
            part2 = np.exp(-q * maturity / 365) * norm.cdf(d1) * (
                        (2 * (rate - q) * maturity / 365) - (d2 * vol * np.sqrt(maturity / 365))) / (
                                2 * (maturity / 365) * vol * np.sqrt(maturity / 365))
            charm = part1 + part2
        except:
            charm = np.nan

        try:
            DvegaDtime = 1
        except:
            DvegaDtime = np.nan
        try:
            fair_value = spot * (np.exp(-q * maturity / 365)) * norm.cdf(d1) - (
                np.exp(-rate * maturity / 365)) * strike * norm.cdf(d2)
            lambdaa = delta * spot / fair_value
        except:
            lambdaa = np.nan

    if Call_Put_Flag == 'Put':
        try:
            delta = np.exp(-rate * maturity / 365) * (norm.cdf(d1) - 1)
        except:
            delta = np.nan
        try:
            theta = ((1 / maturity / 365) * -(spot * vol * np.exp(-q * maturity / 365)) / 2 * np.sqrt(
                maturity / 365) * (
                         np.exp((-d1 ** 2) / 2)) / np.sqrt(2 * 3.14159)) + rate * strike * np.exp(
                -rate * maturity / 365) * norm.cdf(
                -d2) - q * spot * np.exp(rate * maturity / 365) * norm.cdf(-d1)
        except:
            theta = np.nan
        try:
            rho = -strike * maturity / 365 * np.exp(-rate * maturity / 365) * norm.cdf(-d2)
        except:
            rho = np.nan

        try:

            epsilon = strike * (maturity / 365) * np.exp(-q * maturity / 365) * norm.cdf(-d1)
        except:
            epsilon = np.nan

        try:
            part1 = q * (np.exp(-q * maturity / 365)) * norm.cdf(-d1)
            part2 = np.exp(-q * maturity / 365) * norm.cdf(d1) * (
                        (2 * (rate - q) * maturity / 365) - (d2 * vol * np.sqrt(maturity / 365))) / (
                                2 * (maturity / 365) * vol * np.sqrt(maturity / 365))
            charm = part1 + part2
        except:
            charm = np.nan

        try:
            DvegaDtime = 1
        except:
            DvegaDtime = np.nan
        try:
            fair_value = (np.exp(-rate * maturity / 365)) * norm.cdf(-d2) - spot * (
                np.exp(-q * maturity / 365)) * norm.cdf(-d1)
            lambdaa = delta * spot / fair_value
        except:
            lambdaa = np.nan
    if df['Long_Short_Flag'] == 1:
        return pd.Series([delta, gamma, vega, theta, rho, lambdaa, epsilon, vanna, charm, volga, DvegaDtime, veta, color, ultima, speed, zomma])
    else:
        return pd.Series([-delta, -gamma, -vega, -theta, -rho, -lambdaa, -epsilon, -vanna, -charm, -volga, -DvegaDtime, -veta, -color, -ultima, -speed, -zomma])


layout = [html.Div(
        [indicator("#00cc96", "Delta", "delta_indicator",),   #first line indicators: delta, gamma, vega
         indicator("#119DFF", "Gamma", "gamma_indicator",),
         indicator("#EF553B", "Vega", "vega_indicator",),
        ],
        className="row",
    ),
         html.Div(
        [indicator("#00cc96", "Theta", "theta_indicator",),   #second line indicators: theta, rho, veta
         indicator("#119DFF", "Rho", "rho_indicator",),
         indicator("#EF553B", "Veta", "veta_indicator",),
        ],
        className="row",
    ),
         html.Div(
        [indicator("#00cc96", "Speed", "speed_indicator",),   #third line indicators: speed, zomma, color
         indicator("#119DFF", "Zomma", "zomma_indicator",),
         indicator("#EF553B", "Color", "color_indicator",),
        ],
        className="row",
    ),
         html.Div(
        [indicator("#00cc96", "Ultima", "ultima_indicator",),   #fourth line indicators: ultima, lambdaa, epsilon
         indicator("#00cc96", "Lambdaa", "lambdaa_indicator",),
         indicator("#00cc96", "Epsilon", "epsilon_indicator",),
        ],
        className="row",
    ),
         html.Div(
        [indicator("#00cc96", "Vanna", "vanna_indicator", ),   #fifth line indicators: vanna, charm, volga
         indicator("#00cc96", "Charm", "charm_indicator", ),
         indicator("#00cc96", "Volga", "volga_indicator", ),
         ],
        className="row",
    ),
]


# updates delta indicator value based on df updates
@app.callback(Output("delta_indicator", "children"),
             [Input("options_df", "children")],)
def delta_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    print('portfolio', df)
    global result
    result = df.apply(greeks, axis=1).fillna(0)
    print('greeks', result)
    return round(result[0].sum(), 3)

# updates gamma indicator value based on df updates
@app.callback(Output("gamma_indicator", "children"),
             [Input("options_df", "children")],)
def gamma_indicator_callback(df):
    return round(result[1].sum(), 3)


# updates vega indicator value based on df updates
@app.callback(Output("vega_indicator", "children"),
             [Input("options_df", "children")],)
def vega_indicator_callback(df):
    return round(result[2].sum(), 3)


#second line indicators: theta, rho, veta
@app.callback(Output("theta_indicator", "children"),
             [Input("options_df", "children")],)
def theta_indicator_callback(df):
    return round(result[3].sum(), 3)

@app.callback(Output("rho_indicator", "children"),
             [Input("options_df", "children")],)
def rho_indicator_callback(df):
    return round(result[4].sum(), 3)

@app.callback(Output("veta_indicator", "children"),
             [Input("options_df", "children")],)
def veta_indicator_callback(df):
    return round(result[11].sum(), 3)

#third line indicators: speed, zomma, color
@app.callback(Output("speed_indicator", "children"),
             [Input("options_df", "children")],)
def speed_indicator_callback(df):
    return round(result[14].sum(), 3)

@app.callback(Output("zomma_indicator", "children"),
             [Input("options_df", "children")],)
def zomma_indicator_callback(df):
    return round(result[15].sum(), 3)

@app.callback(Output("color_indicator", "children"),
             [Input("options_df", "children")],)
def color_indicator_callback(df):
    return round(result[12].sum(), 3)


#fourth line indicators: ultima, lambdaa, epsilon
@app.callback(Output("ultima_indicator", "children"),
             [Input("options_df", "children")],)
def ultima_indicator_callback(df):
    return round(result[13].sum(), 3)

@app.callback(Output("lambdaa_indicator", "children"),
             [Input("options_df", "children")],)
def lambdaa_indicator_callback(df):
    return round(result[5].sum(), 3)

@app.callback(Output("epsilon_indicator", "children"),
             [Input("options_df", "children")],)
def epsilon_indicator_callback(df):
    return round(result[6].sum(), 3)

#fifth line indicators: vanna, charm, volga
@app.callback(Output("vanna_indicator", "children"),
             [Input("options_df", "children")],)
def vanna_indicator_callback(df):
    return round(result[7].sum(), 3)

@app.callback(Output("charm_indicator", "children"),
             [Input("options_df", "children")],)
def charm_indicator_callback(df):
    return round(result[8].sum(), 3)

@app.callback(Output("volga_indicator", "children"),
             [Input("options_df", "children")],)
def volga_indicator_callback(df):
    return round(result[9].sum(), 3)

