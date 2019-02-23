import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import plotly.plotly as py
from plotly import graph_objs as go
import math
from apps import greeks, payoff, volatility, hedging, stresstest
from strategy import sfManager

server = flask.Flask(__name__)

app = dash.Dash(__name__, server=server)

my_strategy = pd.DataFrame(columns=[])
df = sfManager(my_strategy)