import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from apps import basics, hedging, stresstest, greeks, impliedvolatility
from app import app, df_to_table, Graph, update_graph, indicator, marks
from strategy import stmanager, columns
from tickers import data

options_data = data



def modal():
    return   html.Div(
        html.Div(
            html.Div(
                [html.Div(
                    [html.Span(
                        "Choose your option",
                        style={"color": "#506784", "fontWeight": "bold", "fontSize": "20",},),
                    html.Span(
                        "×",
                        id="options_modal_close",
                        n_clicks=0,
                        style={ "float": "right", "cursor": "pointer","marginTop": "0", "marginBottom": "17",},),],
                    className="row",
                    style={"borderBottom": "1px solid #C8D4E3"},),

                    dash_table.DataTable(
                        id='data_table',
                        columns=[{"name": i, "id": i, "deletable": True} for i in options_data.columns],
                        data=options_data.to_dict('records'),
                        filtering=True,
                        sorting=True,
                        sorting_type="multi",
                        row_selectable="single",
                        selected_rows=[],
                        pagination_mode="fe",
                        pagination_settings={
                            "displayed_pages": 1,
                            "current_page": 0,
                            "page_size": 10,
                        },
                        navigation="page",
                    ),

                    # submit button
                    html.Div(html.Span("Long", id="long_option", n_clicks=0), className="button button--primary add"),
                    html.Div(html.Span("Short", id="short_option", n_clicks=0), className="button button--primary add"),
                ],
                className="modal-content",
                style={"textAlign": "center"},
            ),
            className="modal",

        ),
        id="options_modal",
        style={"display": "none"},
    )


app.layout = html.Div(
    [
        # header
        html.Div([
            html.Span("Derivative Analyzer", className='app-title'),
            html.Div(
                html.Img(src='https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png', height="100%"),
                style={"float": "right", "height": "100%"})
        ],
            className="row header"
        ),


        # tabs
        html.Div([
            dcc.Tabs(
                id="tabs",
                style={"verticalAlign": "middle"},
                children=[
                    dcc.Tab(label="Basics", value="basics_tab", ),
                    dcc.Tab(label="Greeks", value="greeks_tab", ),
                    dcc.Tab(label="Implied Volatility", value="impliedvolatility_tab", ),
                    dcc.Tab(label="Hedging strategy", value="hedging_tab", ),
                    dcc.Tab(id="stresstest_tab", label="Stress test", value="stresstest_tab", ),
                ],
                value="leads_tab",
            )
        ],
            className="row tabs_div",
            style={'height': '70px'}
        ),


        html.Div([
            # add option button
            html.Div(
                html.Button("Add new", id="add_button", n_clicks=0,),
                className="two columns",
                style={'margin-left': '40px', 'width':'127px'},#'backgroundColor': 'rgb(17,157,255)'
            ),
            # clear button
            html.Div(
                html.Button("Clear", id="clear_button", n_clicks=0,),
                className="two columns",
                style={'margin-left': '20px'}
            ),
            # help button
            html.Div(
                html.Button("Help", id='help_button'),
                style={'float':'right', 'margin-right':'40px'}
            )
            ],
            className = "row",
            style = {"marginBottom": "10"},
        ),

        # strategy tble
        html.Div([html.P('My current strategy: ', style = {'margin-left': '40px'}),
                  html.Div(
                      id="strategy_table",
                      className="row",
                      style={"maxHeight": "350px", "overflowY": "scroll", "padding": "8", "marginTop": "5",
                             "backgroundColor": "white", "border": "1px solid #C8D4E3", "borderRadius": "3px",
                             'margin-left': '40px', 'margin-right': '40px'},
                  ),
        ]),


        modal(),
        html.Div(stmanager.get_options().to_json(orient="split"), id="options_df", style={"display": "none"},),

        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),
    ],
    className="row",
    style={"margin": "0%"},
)


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "basics_tab":
        return basics.layout
    elif tab == "hedging_tab":
        return hedging.layout
    elif tab == "impliedvolatility_tab":
        return impliedvolatility.layout
    elif tab == "greeks_tab":
        return greeks.layout
    elif tab == "stresstest_tab":
        return stresstest.layout
    else:
        return basics.layout


# hide/show modal
@app.callback(Output("options_modal", "style"),
              [Input("add_button", "n_clicks")],)
def display_options_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


long_num = 0
short_num = 0
# add option to the strategy
@app.callback(Output('options_df', 'children'),
              [Input('data_table', 'selected_rows'),
               Input("long_option", "n_clicks"),
               Input("short_option", "n_clicks"),])
def update_graph(selected_row, n1, n2):
    global long_num
    global short_num
    if n1 > long_num:
        long_num = long_num + 1
        temp = options_data.iloc[selected_row[0]].to_dict()
        temp['Long_Short_Flag'] = 1
        print(temp)
        stmanager.add_option(temp)
        df = stmanager.get_options()
        print('current strategy: ', df)
        return df.to_json(orient="split")
    elif n2 > short_num:
        short_num = short_num + 1
        temp = options_data.iloc[selected_row[0]].to_dict()
        temp['Long_Short_Flag'] = -1
        print(temp)
        stmanager.add_option(temp)
        df = stmanager.get_options()
        print('current strategy: ', df)
        return df.to_json(orient="split")
    else:
        df = stmanager.get_options()
        return df.to_json(orient="split")


# strategy table callback
@app.callback(Output("strategy_table", "children"),
             [Input("options_df", "children")],)
def strategy_table_callback(df):
    df = pd.read_json(df, orient="split")
    return df_to_table(df)


@app.callback(Output("add_button", "n_clicks"),
             [Input("options_modal_close", "n_clicks"),
              Input("long_option", "n_clicks"),
              Input("short_option", "n_clicks")],)
def close_modal_callback(n, n2, n3):
    return 0


@app.callback(Output("options_df", "n_clicks"),
             [Input("clear_button", "n_clicks"),],)
def clear_strategy_callback(n):
    if n > 0:
        stmanager.clear_options()
        df = stmanager.get_options()
        print(df)
        return df.to_json(orient="split")


if __name__ == "__main__":
    app.run_server(debug=True)





