import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from app import app, indicator, Graph, update_graph, marks
from scipy.stats import norm

def delta_gamma_calculation(df):
    rate = 0.015
    q = 0
    spot = df['Spot Price']
    strike = df['strike']
    vol = df['impliedVolatility']
    maturity = df['days to expiration']
    Call_Put_Flag = df['Call_Put_Flag']
    d1 = (np.log(spot / strike) + (maturity / 365) * (rate - q + (vol ** 2) / 2)) / (vol * np.sqrt(maturity / 365))
    gamma = ((np.exp(-q * maturity / 365) / (spot * vol * np.sqrt(maturity / 365))) * 1 / np.sqrt(2 * np.pi)) * np.exp(
        (-d1 ** 2) / 2)

    if Call_Put_Flag == 'Call':
        try:
            delta = np.exp(-q * maturity / 365) * norm.cdf(d1)
        except:
            delta = np.nan

    if Call_Put_Flag == 'Put':
        try:
            delta = np.exp(-rate * maturity / 365) * (norm.cdf(d1) - 1)
        except:
            delta = np.nan
    if df['Long_Short_Flag']==1:
        return pd.Series([delta, gamma])
    else:
        return pd.Series([-delta, -gamma])


def hedge_suggest(df, deltanut, gammanut, option_needed_delta, option_needed_gamma):
    result = df.apply(delta_gamma_calculation, axis=1)
    port_delta = result[0].sum()
    port_gamma = result[1].sum()
    number_of_contracts = len(df)
    if deltanut == 1:
        if gammanut == 0:
            type = "delta nuetral"
            stock_needed = port_delta * 100 * number_of_contracts
            if port_delta > 0:
                result = "Sell " + str(np.round(stock_needed, 2)) + " stocks"
            else:
                result = "Buy " + str(np.round(stock_needed, 2)) + " stocks"
        elif gammanut == 1:
            type = "gamma and delta nuetral"
            option_needed = -1 * port_gamma / option_needed_gamma
            new_delta = option_needed * option_needed_delta + port_delta
            stock_needed = new_delta * 100 * (number_of_contracts + option_needed)
            if new_delta > 0 and option_needed > 0:
                result = "Sell " + str(np.round(np.abs(stock_needed), 2)) + " stocks and buy " + str(np.round(np.abs(option_needed), 4)) + " option(s)"
            elif new_delta < 0 and option_needed > 0:
                result = "buy " + str(np.round(stock_needed, 2)) + " stocks and " + str(np.round(np.abs(option_needed), 4)) + " option(s)"
            elif new_delta < 0 and option_needed < 0:
                result = "buy " + str(np.round(stock_needed, 2)) + " stocks and sell " + str(np.round(np.abs(option_needed), 4)) + " option(s)"
            else:
                result = "Sell " + str(np.round(np.abs(stock_needed), 2)) + " stocks and sell " + str(np.round(np.abs(option_needed), 4)) + " option(s)"

    else:
        if gammanut == 0:
            type = "You need to pick a hedging strategy"
            result = 'No strategy'
        else:
            type = "gamma nuetral"
            option_needed = -1 * port_gamma / option_needed_gamma
            if option_needed < 0:
                result = "sell " + str(np.round(np.abs(option_needed), 4)) + " option(s)"
            else:
                result = "Buy " + str(np.round(np.abs(option_needed), 4)) + " option(s)"

    return type, result


layout = html.Div(
    [
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Div([
                html.Label('Strategy settings:'),
                dcc.Checklist(
                    id='strategy_settings',
                    options=[
                        {'label': 'Delta', 'value': 'delta'},
                        {'label': 'Gamma', 'value': 'gamma'},
                    ],
                    values=['delta',],
                    labelStyle={'display': 'inline-block'}
                )
            ],
                className='six columns'),
        html.Div([
            html.Div([
                html.Div([
                    html.Label('Hedging option delta:'),
                    dcc.Slider(
                        id='option_needed_delta',
                        min=-1, max=1, step=0.1, value=0.5,
                        marks= marks,
                    ),
                ]),
                html.Div([
                    html.Label('Hedging option gamma:'),
                    dcc.Slider(
                        id='option_needed_gamma',
                        min=-1, max=1, step=0.1, value=0.2,
                        marks= marks,
                    ),

                ],style = {'margin-top': '30px'},),
            ],
                className='four columns'),
        ],
            className='row',
            style={'height': '140px'}
        ),

        html.Div(
            [html.P('Hedging Strategy', className="twelve columns indicator_text"),
             html.P(id='hedging_strategy', className="indicator_value"), ],
            className="four columns indicator",
            style={'height': '150px'}
        ),

    ],
    style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-family': 'overpass',
        'background-color': '#F3F3F3',
        'padding': '40',
        'padding-top': '20',
        'padding-bottom': '20',
    },
)

@app.callback(Output('hedging_strategy', 'children'),
              [Input('strategy_settings', 'values'),
               Input('option_needed_delta', 'value'),
               Input('option_needed_gamma', 'value'),
               Input("options_df", "children")],
              )
def hedging_strategy_callback(strategy_settings, option_needed_delta, option_needed_gamma, df):
    deltanut = 0
    gammanut = 0
    if 'delta' in strategy_settings:
        deltanut = 1
    if 'gamma' in strategy_settings:
        gammanut = 1
    df = pd.read_json(df, orient="split")
    result_hedging = hedge_suggest(df, deltanut, gammanut, option_needed_delta, option_needed_gamma)
    return result_hedging[1]



