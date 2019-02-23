import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import plotly.plotly as py
from plotly import graph_objs as go
import math
from app import app, my_strategy , df

layout = html.Div([
    dcc.Graph(id='my-graph')
], className="container")

app.config['suppress_callback_exceptions']=True

@app.callback(Output('my-graph', 'figure'))

def update_graph():
    return {
        'data': [{
            'x': [1,2,3,4,5],
            'y': [1,2,3,4,5],
            'line': {
                'width': 3,
                'shape': 'spline'
            }
        }],
        'layout': {
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        }
    }

if __name__ == '__main__':
    app.run_server()

