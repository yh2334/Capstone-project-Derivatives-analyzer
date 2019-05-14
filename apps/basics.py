import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from app import app, indicator, Graph

app.config['suppress_callback_exceptions']=True


def update_graph(xvalues, yvalues, xtitle, ytitle):
    trace = go.Scatter(
        x = xvalues,
        y = yvalues,
        mode='lines',
        opacity=0.7,)
    layout = go.Layout(
        xaxis = {'title': xtitle},
        yaxis = {'title': ytitle},
        margin = {'l': 40, 'b': 40, 't': 10, 'r': 10},
        legend = {'x': 0, 'y': 1},
        annotations=[dict(x=xvalues[50], y=yvalues[50], xref='x', yref='y', text='Now', showarrow=True)],
        hovermode = 'closest')
    return {"data": [trace], "layout": layout}


def options_payoff(Call_Put_Flag, Long_Short_Flag, strike_price, spot, premium):
    sT = np.arange(spot - 50, spot + 50, 1)
    if Long_Short_Flag == 'Long':
        if Call_Put_Flag == 'Call':
            def payoff(sT, strike_price, premium):
                return np.where(sT > strike_price, sT - strike_price, 0) - premium
            payoff = payoff(sT, strike_price, premium)
        else:
            def payoff(sT, strike_price, premium):
                return np.where(sT < strike_price, strike_price - sT, 0) - premium
            payoff = payoff(sT, strike_price, premium)
    else:
        if Call_Put_Flag == 'Call':
            def payoff(sT, strike_price, premium):
                return np.where(sT > strike_price, -sT + strike_price, 0) + premium
            payoff = payoff(sT, strike_price, premium)
        else:
            def payoff(sT, strike_price, premium):
                return np.where(sT < strike_price, -strike_price + sT, 0) + premium
            payoff = payoff(sT, strike_price, premium)
    return payoff


def payoff_intrinsicValue(df):
    payoff = np.zeros(100)
    premium_paid = 0
    for i in range(len(df)):
        strike = df['strike'][i]
        spot = df['Spot Price'][i]
        premium = (df['ask'][i] + df['bid'][i]) / 2
        long_short = df['Long_Short_Flag'][i]
        call_put = df['Call_Put_Flag'][i]

        payoff1 = options_payoff(call_put, long_short, strike, spot, premium)
        payoff = payoff1 + payoff
        if long_short == 1:
            premium_paid = premium_paid + premium
        else:
            premium_paid = premium_paid - premium

    intrinsic_value = payoff[50] + premium_paid
    sT = np.arange(spot - 50, spot + 50, 1)
    return sT.tolist(), payoff.tolist(), intrinsic_value


layout = [html.Div(Graph('Payoff', 'payoff'),className="row",style={"marginTop": "5px"},),
          html.Div(indicator("#00cc96", "Intrinsic Value", "intrinsic_value",), className="row", style={"marginTop": "5px"},)]


# payoff graph callback
@app.callback(Output("payoff", "figure"),
              [Input("options_df", "children")],)
def payoff_graph_callback(df):
    df = pd.read_json(df, orient="split")
    result_basics = payoff_intrinsicValue(df)
    return update_graph(result_basics[0], result_basics[1], 'Stock Price', 'Profit and Loss')


# intrinsic value callback
@app.callback(Output("intrinsic_value", "children"),
             [Input("options_df", "children")],)
def intrinsic_value_callback(df):
    df = pd.read_json(df, orient="split")
    result_basics = payoff_intrinsicValue(df)
    return round(result_basics[2], 3)
