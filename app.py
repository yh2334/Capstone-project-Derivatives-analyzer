import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
from strategy import StrategyManager
import dash_html_components as html
import plotly.graph_objs as go

server = flask.Flask(__name__)

app = dash.Dash(__name__, server=server)

external_css = ["https://fonts.googleapis.com/css?family=Overpass:300,300i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css",
                "https://use.fontawesome.com/releases/v5.2.0/css/all.css",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",
                "https://fonts.googleapis.com/css?family=Dosis",
                "https://fonts.googleapis.com/css?family=Open+Sans",
                "https://fonts.googleapis.com/css?family=Ubuntu",
                "https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


# returns indicator div
def indicator(color, text, id_value):
    return html.Div(
        [html.P(
            text,
            className="twelve columns indicator_text"
            ),
        html.P(
            id=id_value,
            className="indicator_value"
            ),
        ],
        className="four columns indicator",
    )


# returns graph div
def Graph(text, id_value):
    return html.Div(
        [ html.P(text),
          dcc.Graph(
            id=id_value,
            config=dict(displayModeBar=False),
            style={"height": "89%", "width": "98%"},
            ),
            ],
        className="six columns chart_div",)


# returns updated graph in callbacks
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
        hovermode = 'closest')
    return {"data": [trace], "layout": layout}


# return html Table with dataframe values
def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +
        # Body
        [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
            for i in range(len(df))
        ]
    )


marks = {-1: {'label': '-1'},-0.7: {'label': '-0.7'},0: {'label': '0'},0.7: {'label': '0.7'},1: {'label': '1'},
         -0.9: {'label': '-0.9'},-0.8: {'label': '-0.8'},0.1: {'label': '0.1'},0.2: {'label': '0.2'},0.3: {'label': '0.3'},
         -0.6: {'label': '-0.6'},-0.7: {'label': '-0.7'},0.4: {'label': '0.4'},0.5: {'label': '0.5'},0.6: {'label': '0.6'},
         -0.5: {'label': '-0.5'},-0.4: {'label': '-0.4'},0.8: {'label': '0.8'},0.9: {'label': '0.5'},-0.3: {'label': '-0.3'},
        -0.2: {'label': '-0.2'},-0.1: {'label': '-0.1'}}

