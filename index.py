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
from app import app, my_strategy , df


def modal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        # modal header
                        html.Div(
                            [
                                html.Span(
                                    "New Option",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),

                                html.Span(
                                    "×",
                                    id="option_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="row",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),

                        # modal form
                        html.Div(
                            [
                                # left div
                                html.Div(
                                    [
                                        html.P(
                                            [
                                                "Type"
                                            ],
                                            style={
                                                "float": "left",
                                                "marginTop": "4",
                                                "marginBottom": "2",
                                            },
                                            className="row",
                                        ),

                                        dcc.Dropdown(
                                            id="new_option_type",
                                            options=[
                                                {
                                                    "label": "Call",
                                                    "value": "Call",
                                                },
                                                {
                                                    "label": "Put",
                                                    "value": "Put",
                                                },
                                            ],
                                            clearable=False,
                                            value="Prospecting",
                                        ),
                                    ]
                                )
                            ]
                        ),


                        # submit button

                        html.Span(
                            "Submit",
                            id="submit_new_option",
                            n_clicks=0,
                            className="button button--primary add"
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id= "option_modal",
        style={"display": "none"},
    )

app.layout = html.Div(
    [  # header
        html.Div(
            html.Span("Derivative Analyzer", className='app-title'),
            className="row header"
        ),


        #option adding&clearing div
        html.Div(
            html.Span(
                children = [
                    html.Span("Add option", id="new_option", n_clicks=0, className="button button--primary add"),
                    html.Span("Clear", id="clear", n_clicks=0, className="button button--primary clear")
                ],

            className="two columns",
            style={"float": "left"})
        ),


        #tabs div

        html.Div([
            dcc.Tabs(
                id="tabs",
                style={"height": "20", "verticalAlign": "middle"},
                vertical=True,
                children=[
                    dcc.Tab(label="Payoff", value="payoff_tab"),
                    dcc.Tab(label="Greeks", value="greeks_tab"),
                    dcc.Tab(label="Volatility", value="volatility_tab"),
                    dcc.Tab(label="Hedging", value="hedging_tab"),
                    dcc.Tab(id="stresstest_tab", label="Stress test", value="stresstest_tab"),
                ],
                value="leads_tab",
            )
        ], className="row tabs_div"
        ),

        html.Div(id="option_df"),
        html.Div(id="option_df2"),

        # tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),
        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css", rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",
            rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css",
            rel="stylesheet"),

        modal()

    ],

    className="row",
    style={"margin": "0%"},

)


# hide/show modal
@app.callback(Output("option_modal", "style"), [Input("new_option", "n_clicks")])
def display_option_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}



# reset to 0 add button n_clicks property
@app.callback(Output("new_option", "n_clicks"),
    [Input("option_modal_close", "n_clicks"),
     Input("submit_new_option", "n_clicks"),],)
def close_modal_callback(n, n2):
    return 0


# add button
@app.callback(
    Output("option_df", "children"),
    [Input("submit_new_option", "n_clicks")],
    [State("new_option_type", "value"),]
)

def add_option_callback(
    n_clicks, type

):
    if n_clicks > 0:
        if type == "":
            name = "Not named yet"
        query = {
            "Type": type,
        }

        df.add_option(query)

#clear button
@app.callback(Output("option_df2", "children"), [Input("clear", "n_clicks")])
def clear_button_callback(n):
    if n > 0:
        df.clear()



@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "stresstest_tab":
        return stresstest.layout

    elif tab == "greeks_tab":
        return greeks.layout

    elif tab == "volatility_tab":
        return volatility.layout

    elif tab == "hedging_tab":
        return hedging.layout

    else:
        return payoff.layout


if __name__ == "__main__":
    app.run_server(debug=True)