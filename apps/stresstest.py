import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from app import app, indicator, Graph
from scipy.stats import norm
import plotly.graph_objs as go
import warnings


def stressTestForOne(df, fre, spot, upOrDown, percentChange, function, vol):
    if upOrDown == 'down':
        vol = -vol
    change = percentChange/(fre*100)
    change1 = percentChange / 100
    spots = []
    deltas = []
    vegas = []
    gammas = []
    thetas = []
    values = []
    rate = 0.015
    q = 0
    strike = df['strike']
    type = df['Call_Put_Flag']
    mat = df['days to expiration']
    for i in range(fre):
        if(upOrDown == 'down' and function == 'linear'):
            spot = (1-change)*spot
        elif(upOrDown == 'up' and function == 'linear'):
            spot = (1+change)*spot
        elif(upOrDown == 'down' and function == 'exp'):
            spot_T=spot*(1-change1)
            spot_T_x=np.log(spot*change1)-1
            x_intervals=spot_T_x/fre
            price=(i*x_intervals)**2+spot
        elif(upOrDown == 'up' and function == 'exp'):
            spot_T=spot*(1-change1)
            spot_T_x=np.log(spot*change1)-1
            x_intervals=spot_T_x/fre
            price=(i*x_intervals)**2+spot
        elif(upOrDown == 'down' and function == 'quadratic'):
            spot_T=spot*(1-change1)
            spot_T_x=np.sqrt(spot*change1)
            x_intervals=spot_T_x/fre
            price=(i*x_intervals)**2+spot
        elif(upOrDown == 'up' and function == 'quadratic'):
            spot_T=spot*(1+change1)
            spot_T_x=np.sqrt(spot*change1)
            x_intervals=spot_T_x/fre
            price=(i*x_intervals)**2+spot
        if(function == 'linear'):
            spots.append(spot)
        elif(function == 'quadratic' or function == 'exp'):
            spots.append(price)
        maturity = mat - i
        d1 = (np.log(spot / strike) + (maturity / 365) * (rate - q + (vol ** 2) / 2)) / (vol * np.sqrt(maturity / 365))
        d2 = d1 - vol * np.sqrt(maturity / 365)
        deltas.append(np.exp(-q * maturity / 365) * norm.cdf(d1))
        thetas.append(((1 / (maturity / 365)) * -((spot * vol * np.exp(-q * maturity / 365))) / 2 * np.sqrt(maturity / 365)) * (np.exp((-d1 ** 2) / 2)) / np.sqrt(2 * 3.14159) - rate * strike * np.exp( -rate * maturity / 365) * norm.cdf(d2) + q * spot * np.exp(rate * maturity / 365) * norm.cdf(d1))
        gammas.append(((np.exp(-q * maturity / 365) / (spot * vol * np.sqrt(maturity / 365))) * 1 / np.sqrt(2 * np.pi)) * np.exp((-d1 ** 2) / 2))
        vegas.append((((spot * np.exp(-q * maturity / 365)) * np.sqrt(maturity / 365)) / 100) * 1 / np.sqrt(2 * 3.14159) * np.exp((-d1 ** 2) / 2))
        if type == 'Call':
            values.append(spot*(np.exp(-q * maturity / 365))*norm.cdf(d1)-(np.exp(-rate * maturity / 365))*strike*norm.cdf(d2))
        else:
            values.append((np.exp(-rate * maturity / 365))*norm.cdf(-d2)-spot*(np.exp(-q * maturity / 365))*norm.cdf(-d1))

    return spots, deltas, vegas, gammas, thetas, values


def stressTest(df, fre, spot, upOrDown, percentChange, function,  vol):
    spots = [0 for i in range(fre)]
    deltas = [0 for i in range(fre)]
    vegas = [0 for i in range(fre)]
    gammas = [0 for i in range(fre)]
    thetas = [0 for i in range(fre)]
    values = [0 for i in range(fre)]
    for i in range(len(df)):
        s, d, v, g, t, value= stressTestForOne(df.iloc[i], fre, spot, upOrDown, percentChange, function,  vol)
        spots = [spots[j]+s[j] for j in range(0, len(spots))]
        deltas = [deltas[j]+d[j] for j in range(0, len(deltas))]
        vegas = [vegas[j]+v[j] for j in range(0, len(vegas))]
        gammas = [gammas[j]+g[j] for j in range(0, len(gammas))]
        thetas = [thetas[j]+t[j] for j in range(0, len(thetas))]
        values = [values[j]+value[j] for j in range(0, len(values))]
    return spots, deltas, vegas, gammas, thetas, values


def update_graph(xvalues, yvalues, xtitle, ytitle):
    trace = go.Scatter(
        x = xvalues,
        y = yvalues,
        mode='lines+markers',
        opacity=0.7,)
    layout = go.Layout(
        xaxis = {'title': xtitle},
        yaxis = {'title': ytitle},
        margin = {'l': 80, 'b': 40, 't': 10, 'r': 10},
        legend = {'x': 0, 'y': 1},
        hovermode = 'closest')
    return {"data": [trace], "layout": layout}


layout = [
    html.Div(
        [html.Span('The max limit for the frequency is: ', style={'margin-left': '40px', 'margin-right': '40px'}),
         html.Span(id='max_limit')],),

    # top controls
    html.Div(
        [
             html.Div([
                html.Label('Enter a frequency:'),
                dcc.Input(
                    id='frequency_input',
                    placeholder='Enter a frequency...',
                    type= 'number',
                    value= 1)],
                className="two columns",
                style={'margin-left': '40px'}
            ),

            html.Div([
                html.Label('Up or Down'),
                dcc.Dropdown(
                    id="direction_dropdown",
                    options=[
                        {"label": "Up", "value": "up"},
                        {"label": "Down", "value": "down"},
                    ],
                    placeholder="Select price direction",
                    value="up",
                    clearable=False,
                )],
                className="two columns",
            ),

            html.Div([
                html.Label('Price Percentage change'),
                dcc.Dropdown(
                    id="percentchange_dropdown",
                    options=[
                        {"label": 10*(i+1), "value": 10*(i+1)} for i in range(10)
                    ],
                    value= 10,
                    clearable=False,
                )],
                className="two columns",
            ),

            html.Div([
                html.Label('Volatility Percentage change'),
                dcc.Dropdown(
                    id="volpct_dropdown",
                    options=[
                        {"label": 5, "value": 5},
                        {"label": 10, "value": 10},
                        {"label": 20, "value": 20},
                        {"label": 30, "value": 30},
                    ],
                    value= 10,
                    clearable=False,
                )],
                className="two columns",
            ),

            html.Div([
                html.Label('Choose a method'),
                dcc.Dropdown(
                    id="method_dropdown",
                    options=[
                        {"label": "linear", "value": "linear"},
                        {"label": "exp", "value": "exp"},
                        {"label": "quadratic", "value": "quadratic"},
                    ],
                    placeholder="Select a method",
                    value="linear",
                    clearable=False,
                )],
                className="two columns",
                style = {'height':'100px'}
            ),
        ]
    ),

    #graphs
    html.Div(
        html.Div(
            [Graph("Delta vs Price", "delta_vs_price"),
             Graph("Gamma vs Price", "gamma_vs_price")
        ],
        className="row",
        style={"marginTop": "5px"},
        ),
    ),

    html.Div(
        html.Div(
            [Graph("Theta vs Price", "theta_vs_price"),
             Graph("Vega vs Price", "vega_vs_price"),
        ],
        className="row",
        style={"marginTop": "5px"},
        ),
    ),

    html.Div(
        html.Div(
            [Graph("Value vs Price", "value_vs_price"),
        ],
        className="row",
        style={"marginTop": "5px"},
        ),
    ),
    ]


@app.callback(Output('max_limit', 'children'),
              [Input("options_df", "children")],)
def max_limit_callback(df):
    df = pd.read_json(df, orient="split")
    print("The max limit for the frequency is: ", df['days to expiration'][0])
    return df['days to expiration'].max()


@app.callback(Output('delta_vs_price', 'figure'),
              [Input('frequency_input', 'value'),
               Input('direction_dropdown', 'value'),
               Input('percentchange_dropdown', 'value'),
               Input('method_dropdown', 'value'),
               Input('volpct_dropdown', 'value'),
               Input("options_df", "children")],)
def delta_vs_price_callback(fre, upOrDown, percentChange, function, volpct, df):
    df = pd.read_json(df, orient="split")
    spot = df['Spot Price'][0]
    result_st = stressTest(df, fre, spot, upOrDown, percentChange, function, volpct)
    print(result_st[0])
    print(result_st[1])
    return update_graph(result_st[0], result_st[1], 'Price', 'Delta')

@app.callback(Output('gamma_vs_price', 'figure'),
              [Input('frequency_input', 'value'),
               Input('direction_dropdown', 'value'),
               Input('percentchange_dropdown', 'value'),
               Input('method_dropdown', 'value'),
               Input('volpct_dropdown', 'value'),
               Input("options_df", "children")], )
def gamma_vs_price_callback(fre, upOrDown, percentChange, function, volpct, df):
    df = pd.read_json(df, orient="split")
    spot = df['Spot Price'][0]
    result_st = stressTest(df, fre, spot, upOrDown, percentChange, function, volpct)
    return update_graph(result_st[0], result_st[2], 'Price', 'Gamma')

@app.callback(Output('theta_vs_price', 'figure'),
              [Input('frequency_input', 'value'),
               Input('direction_dropdown', 'value'),
               Input('percentchange_dropdown', 'value'),
               Input('method_dropdown', 'value'),
               Input('volpct_dropdown', 'value'),
               Input("options_df", "children")], )
def theta_vs_price_callback(fre, upOrDown, percentChange, function, volpct, df):
    df = pd.read_json(df, orient="split")
    spot = df['Spot Price'][0]
    result_st = stressTest(df, fre, spot, upOrDown, percentChange, function, volpct)
    return update_graph(result_st[0], result_st[3], 'Price', 'Theta')

@app.callback(Output('vega_vs_price', 'figure'),
              [Input('frequency_input', 'value'),
               Input('direction_dropdown', 'value'),
               Input('percentchange_dropdown', 'value'),
               Input('method_dropdown', 'value'),
               Input('volpct_dropdown', 'value'),
               Input("options_df", "children")], )
def vega_vs_price_callback(fre, upOrDown, percentChange, function, volpct, df):
    df = pd.read_json(df, orient="split")
    spot = df['Spot Price'][0]
    result_st = stressTest(df, fre, spot, upOrDown, percentChange, function, volpct)
    return update_graph(result_st[0], result_st[4], 'Price', 'Veta')

@app.callback(Output('value_vs_price', 'figure'),
              [Input('frequency_input', 'value'),
               Input('direction_dropdown', 'value'),
               Input('percentchange_dropdown', 'value'),
               Input('method_dropdown', 'value'),
               Input('volpct_dropdown', 'value'),
               Input("options_df", "children")], )
def vega_vs_price_callback(fre, upOrDown, percentChange, function, volpct, df):
    df = pd.read_json(df, orient="split")
    spot = df['Spot Price'][0]
    result_st = stressTest(df, fre, spot, upOrDown, percentChange, function, volpct)
    return update_graph(result_st[0], result_st[5], 'Price', 'Value')
