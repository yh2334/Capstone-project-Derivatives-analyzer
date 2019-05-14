# Import required libraries

import datetime as dt
from numpy import array
import pandas as pd
import plotly.plotly as py
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from tickers import tickers
from app import app
from datetime import datetime
from py_vollib.black_scholes_merton.implied_volatility import *
from options_data import optionsdata


# Get volatility matrix
def impliedVolatility_calculation(data,  call=True, put=False, rf_interest_rate=0.0, dividend_rate=0.0, market=True):
    if call and put:
        raise Exception('Must specify either call or put.')
    if not call and not put:
        raise Exception('Must specify either call or put.')
    if call:
        flag = 'c'
        typ = 'Call'
    if put:
        flag = 'p'
        typ = 'Put'

    # Filter dataframe
    df = data[data['Call_Put_Flag'] == typ]
    df.reset_index(inplace=True)
    df.set_index('contractSymbol', inplace=True)
    vals = []

    # Get columns
    if typ == 'Call':
        premiums = df['ask']  # Always assume user wants to get filled pricev
    else:
        premiums = df['bid']

    if not market:
        premiums = df['lastPrice']
    for i in range(len(df)):
        underlying = float(df['lastPrice'][i])
        expd = (df['expiration'][i] - datetime.now()).days
        exps = (df['expiration'][i] - datetime.now()).seconds
        exp = (expd * 24. * 3600. + exps) / (365. * 24. * 3600.)
        P = premiums[i]
        S = underlying
        K = df['strike'][i]
        t = exp
        r = rf_interest_rate / 100
        q = dividend_rate / 100
        try:
            val = implied_volatility(P, S, K, t, r, q, flag)
            vals.append([float(df['strike'][i]),exp, val])
        except:
            val = 0.0
            vals.append([float(df['strike'][i]),exp, val])

    vals = array(vals).T

    return vals[0], vals[1], vals[2]


# Make implied volatility layout
layout = html.Div([
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Div([
            html.Div([
                html.Label('Select ticker:'),
                dcc.Dropdown(
                    id='ticker_dropdown',
                    options=tickers,
                    value='SPY',
                ),
            ],
                className='six columns',
            ),
            html.Div([
                html.Label('Option settings:'),
                dcc.RadioItems(
                    id='option_selector',
                    options=[
                        {'label': 'Call', 'value': 'call'},
                        {'label': 'Put', 'value': 'put'},
                    ],
                    value='call',
                    labelStyle={'display': 'inline-block'},
                ),
                dcc.RadioItems(
                    id='market_selector',
                    options=[
                        {'label': 'Market', 'value': 'market'},
                        {'label': 'Last', 'value': 'last'},
                    ],
                    value='market',
                    labelStyle={'display': 'inline-block'},
                ),
            ],
                className='two columns',
            ),
        ],
            className='row',
            style={'margin-bottom': '10'}
        ),
        html.Div([
            html.Div([
                html.Label('Implied volatility settings:'),
                html.Div([
                    html.Div([
                        html.Label('Risk-free rate (%)'),
                        dcc.Input(
                            id='rf_input',
                            placeholder='Risk-free rate',
                            type='number',
                            value='0.0',
                            style={'width': '125'}
                        )
                    ],
                        style={'display': 'inline-block'}
                    ),
                    html.Div([
                        html.Label('Dividend rate (%)'),
                        dcc.Input(
                            id='div_input',
                            placeholder='Dividend interest rate',
                            type='number',
                            value='0.0',
                            style={'width': '125'}
                        )
                    ],
                        style={'display': 'inline-block'}
                    ),
                ],
                    style={'display': 'inline-block', 'position': 'relative', 'bottom': '10'}
                )
            ],
                className='six columns',
                style={'display': 'inline-block'}
            ),
            html.Div([
                html.Label('Chart settings:'),
                dcc.RadioItems(
                    id='log_selector',
                    options=[
                        {'label': 'Log surface', 'value': 'log'},
                        {'label': 'Linear surface', 'value': 'linear'},
                    ],
                    value='log',
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.Checklist(
                    id='graph_toggles',
                    options=[
                        {'label': 'Flat shading', 'value': 'flat'},
                        {'label': 'Lock camera', 'value': 'lock'}
                    ],
                    values=['flat',  'lock'],
                    labelStyle={'display': 'inline-block'}
                )
            ],
                className='six columns'
            ),
        ],
            className='row'
        ),
        html.Div([
            dcc.Graph(id='iv_surface', style={'max-height': '600', 'height': '60vh'}),
        ],
            className='row',
            style={'margin-bottom': '20'}
        ),


        html.P(
            hidden='',
            id='raw_container',
            style={'display': 'none'}
        ),
        html.P(
            hidden='',
            id='filtered_container',
            style={'display': 'none'}
        )
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


# Cache raw data
@app.callback(Output('raw_container', 'hidden'),
              [Input('ticker_dropdown', 'value')])
def cache_raw_data(ticker):

    global raw_data
    raw_data = optionsdata(ticker)
    print('Loaded raw data')
    return 'loaded'


# Cache filtered data
@app.callback(Output('filtered_container', 'hidden'),
              [Input('raw_container', 'hidden'),
               Input('option_selector', 'value'),
               Input('market_selector', 'value'),
               Input('rf_input', 'value'),
               Input('div_input', 'value')])  # To be split
def cache_filtered_data(hidden, call_or_put, market, rf_interest_rate, dividend_rate):

    if hidden == 'loaded':
        if call_or_put == 'call':
            s, p, i = impliedVolatility_calculation(raw_data, call=True, put=False,rf_interest_rate=float(rf_interest_rate),dividend_rate=float(dividend_rate),market=market)
        else:
            s, p, i = impliedVolatility_calculation(raw_data, call=False, put=True, rf_interest_rate=float(rf_interest_rate),
                                        dividend_rate=float(dividend_rate), market=market)

        df = pd.DataFrame([s, p, i]).T
        global filtered_data
        filtered_data = df[df[2] > 0.0001]  # Filter invalid calculations with abnormally low IV
        print('Loaded filtered data')
        return 'loaded'


# Make main surface plot
@app.callback(Output('iv_surface', 'figure'),
              [Input('filtered_container', 'hidden'),
               Input('ticker_dropdown', 'value'),
               Input('log_selector', 'value'),
               Input('graph_toggles', 'values')],
              [State('graph_toggles', 'values'),
               State('iv_surface', 'relayoutData')])
def make_surface_plot(hidden, ticker, log_selector, graph_toggles,
                      graph_toggles_state, iv_surface_layout):

    if hidden == 'loaded':

        if 'flat' in graph_toggles:
            flat_shading = True
        else:
            flat_shading = False

        trace1 = {
            "type": "mesh3d",
            'x': filtered_data[0],
            'y': filtered_data[1],
            'z': filtered_data[2],
            'intensity': filtered_data[2],
            'autocolorscale': False,
            "colorscale": [
                [0, "rgb(244,236,21)"], [0.3, "rgb(249,210,41)"], [0.4, "rgb(134,191,118)"], [
                    0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"],
            ],
            "lighting": {
                "ambient": 1,
                "diffuse": 0.9,
                "fresnel": 0.5,
                "roughness": 0.9,
                "specular": 2
            },
            "flatshading": flat_shading,
            "reversescale": True,
        }

        layout = {
            "title": "{} Volatility Surface | {}".format(ticker, str(dt.datetime.now())),
            'margin': {
                'l': 10,
                'r': 10,
                'b': 10,
                't': 60,
            },
            'paper_bgcolor': '#FAFAFA',
            "hovermode": "closest",
            "scene": {
                "aspectmode": "manual",
                "aspectratio": {
                    "x": 2,
                    "y": 2,
                    "z": 1
                },
                'camera': {
                    'up': {'x': 0, 'y': 0, 'z': 1},
                    'center': {'x': 0, 'y': 0, 'z': 0},
                    'eye': {'x': 1, 'y': 1, 'z': 0.5},
                },
                "xaxis": {
                    "title": "Strike ($)",
                    "showbackground": True,
                    "backgroundcolor": "rgb(230, 230,230)",
                    "gridcolor": "rgb(255, 255, 255)",
                    "zerolinecolor": "rgb(255, 255, 255)"
                },
                "yaxis": {
                    "title": "Expiry (days)",
                    "showbackground": True,
                    "backgroundcolor": "rgb(230, 230,230)",
                    "gridcolor": "rgb(255, 255, 255)",
                    "zerolinecolor": "rgb(255, 255, 255)"
                },
                "zaxis": {
                    "rangemode": "tozero",
                    "title": "IV (σ)",
                    "type": log_selector,
                    "showbackground": True,
                    "backgroundcolor": "rgb(230, 230,230)",
                    "gridcolor": "rgb(255, 255, 255)",
                    "zerolinecolor": "rgb(255, 255, 255)"
                }
            },
        }

        if (iv_surface_layout is not None and 'lock' in graph_toggles_state):

            try:
                up = iv_surface_layout['scene']['up']
                center = iv_surface_layout['scene']['center']
                eye = iv_surface_layout['scene']['eye']
                layout['scene']['camera']['up'] = up
                layout['scene']['camera']['center'] = center
                layout['scene']['camera']['eye'] = eye
            except:
                pass

        data = [trace1]
        figure = dict(data=data, layout=layout)
        return figure


