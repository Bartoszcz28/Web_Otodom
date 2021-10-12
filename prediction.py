import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA],)

app.layout = html.Div(style={'textAlign': 'center'}, children=[
    dbc.Row(children=[
        dbc.Col(
            html.Span('Surface', style={'font-weight':'700', 'margin-left': '10px', 'margin-bottom': '5px','front-size' :'20px'}),
        ),
            dbc.Col(     
            dcc.Input(id="m2", type="number", placeholder="m2",className='cell_p', value=15),
       )
        ]),
    
    dbc.Row(children=[
        dbc.Col(
            html.Span('Deposit', style={'font-weight':'700', 'margin-left': '10px', 'margin-bottom': '5px','front-size' :'20px'}),
        ),
        dbc.Col(
            dcc.Input(id="deposit", type="number", placeholder="deposit", className='cell_p', value=2000),
        )
    ]),
    dbc.Row(children=[
        dbc.Col(
            html.Span('Number of floors', style={'font-weight':'700', 'margin-left': '10px', 'margin-bottom': '5px','front-size' :'20px'}),
        ),
        dbc.Col(   
            dcc.Input(id="number_of_floors", type="number", placeholder="nr_of_floors", className='cell_p', value=7),
        )
    ]),
    dbc.Row(children=[
        dbc.Col(
            html.Span('Number of rooms', style={'font-weight':'700', 'margin-left': '10px', 'margin-bottom': '5px','front-size' :'20px'}),
        ),
        dbc.Col(
            dcc.Input(id="room_number", type="number", placeholder="room_number", className='cell_p', value=1),
        )
    ]),
    dbc.Row(children=[
        dbc.Col(
            html.Span('Floor', style={'font-weight':'700', 'margin-left': '10px', 'margin-bottom': '5px','front-size' :'20px'}),
        ),
        dbc.Col(
            dcc.Input(id="floor", type="number", placeholder="floor", className='cell_p', value=5),
        ),
    ]),

        dbc.Row(
            dbc.Col(children=[
                html.Button(id='my-button', n_clicks=0, children="Estimated price", className='Estimated_price'),
                html.Br(),
                html.Div(html.H2(id='p_rent_price')),
                html.Br(),
            ]),
            ),
    ])
            
@app.callback(
    [dash.dependencies.Output('p_rent_price', 'children')],
    [dash.dependencies.State('m2', 'value'),
     dash.dependencies.State('deposit', 'value'),
     dash.dependencies.State('number_of_floors', 'value'),
     dash.dependencies.State('room_number', 'value'),
     dash.dependencies.State('floor', 'value')],
    [dash.dependencies.Input('my-button', 'n_clicks')]
    )
    
def get_prediction(m2, deposit, number_of_floors, room_number, floor, n_clicks):
    p_rent_price = (9.30279610e+01 * float(m2) + 1.07124067e-01 * float(deposit) +  1.25732500e+00 * float(number_of_floors) + -7.07839409e+02 * float(room_number) + 3.37884548e+01 * float(floor))
    
    return (round(p_rent_price, 2),)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')