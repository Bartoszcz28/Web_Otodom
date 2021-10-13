import numpy as np
import pandas as pd
import psycopg2
import pandas.io.sql as sqlio
import matplotlib.pyplot as plt
import pylab as pl
import folium
import json
import os
from folium import plugins
# %matplotlib inline

import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from waitress import serve

psql = psycopg2.connect(host='192.168.10.163', port='5432', database='Otodom', user='barto', password='biznes')

cur = psql.cursor()
sql_rent = "select * from Warsaw_rent;"
sql_sell = "select * from Warsaw_sell;"
dat_rent = sqlio.read_sql_query(sql_rent, psql)
dat_sell = sqlio.read_sql_query(sql_sell, psql)
conn = None

lok_sell = dat_sell[["latitude","longitude","price","m2"]]
lok_rent = dat_rent[["latitude","longitude","rent_price","m2"]]

a = 0
for index, row in lok_sell.iterrows():
    if (np.isnan(lok_sell.at[index,'latitude']) or np.isnan(lok_sell.at[index,'longitude']) 
    or np.isnan(lok_sell.at[index,'price']) or np.isnan(lok_sell.at[index,"m2"])):
        lok_sell = lok_sell.drop([index])
        a += 1
print("Drop rows where Nan from table sell: ", a)

b = 0
for index, row in lok_rent.iterrows():
    if (np.isnan(lok_rent.at[index,'latitude']) or np.isnan(lok_rent.at[index,'longitude']) 
    or np.isnan(lok_rent.at[index,'rent_price']) or np.isnan(lok_rent.at[index,"m2"])):
        lok_rent = lok_rent.drop([index])
        b += 1
print("Drop rows where Nan from table rent: ", b)

lok_sell = lok_sell.reset_index(drop=True)
lok_rent = lok_rent.reset_index(drop=True)

max_value_sell_price = lok_sell["price"].max()
min_value_sell_price = lok_sell["price"].min()

print(max_value_sell_price)
print(min_value_sell_price)


max_value_sell_m2 = lok_sell["m2"].max()
min_value_sell_m2 = lok_sell["m2"].min()

max_value_rent_price = lok_rent["rent_price"].max()
min_value_rent_price = lok_rent["rent_price"].min()

max_value_rent_m2 = lok_rent["m2"].max()
min_value_rent_m2 = lok_rent["m2"].min()

def world_new():    
    my_world = folium.Map(
    zoom_start=11,
    location=[52.2380549, 21.0293513], prefer_canvas=True)
    my_world = plugins.MarkerCluster().add_to(my_world)
    return my_world

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA],)

app.layout = html.Div(children=[
dbc.Row(children=[
    dbc.Col(children=[
        html.H2('Flats for sell and rent in Warsaw', style={'text-align': 'center'}),
        html.Iframe(id = 'map', srcDoc = world_new().get_root().render(),
            width = '100%',height = '90%', className='map')],
            width=8, lg={'size': 8,'order': 'first'}
            ),
    dbc.Col(style={'text-align': 'center'}, children=[
        html.H4('Sell', style={'margin-bottom': '10px', 'margin-top': '10px'}),
        dcc.Input(id="Price_MIN_Sell", type="number", placeholder="Price MIN", value=min_value_sell_price,
                  className='cell'),
        dcc.Input(id="Price_MAX_Sell", type="number", placeholder="Price MAX", value=max_value_sell_price,
                  className='cell'),
        html.Button(id='full-button_price_sell', n_clicks=0, children="MAX",
                   className='button-max'),
        dcc.Input(id="m2_MIN_Sell", type="number", placeholder="m2 MIN", value=min_value_sell_m2,
                 className='cell'),
        dcc.Input(id="m2_MAX_Sell", type="number", placeholder="m2 MAX", value=max_value_sell_m2,
                 className='cell'),
        html.Button(id='full-button_m2_sell', n_clicks=0, children="MAX",
                   className='button-max'),
        html.Div(style={'font-weight':'700', 'margin-bottom': '10px'}, children=[
            html.Span('All flats for sell: '),
            html.Span(id='result_Sell'),]),
        html.H4('Rent'),
        dcc.Input(id="Price_MIN_Rent", type="number", placeholder="Price MIN", value=min_value_rent_price,
                 className='cell'),
        dcc.Input(id="Price_MAX_Rent", type="number", placeholder="Price MAX", value=max_value_rent_price,
                 className='cell'),
        html.Button(id='full-button_price_rent', n_clicks=0, children="MAX",
                   className='button-max'),
        dcc.Input(id="m2_MIN_Rent", type="number", placeholder="m2 MIN", value=min_value_rent_m2,
                 className='cell'),
        dcc.Input(id="m2_MAX_Rent", type="number", placeholder="m2 MAX", value=max_value_rent_m2,
                 className='cell'),
        html.Button(id='full-button_m2_rent', n_clicks=0, children="MAX",
                   className='button-max'),
        html.Div(style={'font-weight':'700', 'margin-bottom': '10px'}, children=[
            html.Span('All flats for rent: '),
            html.Span(id='result_Rent'),]),
        html.Button(id='my-button', n_clicks=0, children="Update",
                   className='button-update'),
        dcc.Graph(id="fig",style={'width': '45vh', 'height': '45vh',
                                        "margin-left": "auto", "margin-right": "auto"})
            ], width=8, lg={'size': 4,  "offset": 0, 'order': 'last'}),
        ])
    ])
@app.callback(
    [dash.dependencies.Output('map', 'srcDoc'),
    dash.dependencies.Output('result_Sell', 'children'),
    dash.dependencies.Output('result_Rent', 'children'),
    dash.dependencies.Output('fig', 'figure')],
    [dash.dependencies.Input('my-button', 'n_clicks')],
    [dash.dependencies.State('Price_MIN_Sell', 'value'),
     dash.dependencies.State('Price_MAX_Sell', 'value'),
     dash.dependencies.State('m2_MIN_Sell', 'value'),
     dash.dependencies.State('m2_MAX_Sell', 'value'),
     dash.dependencies.State('Price_MIN_Rent', 'value'),
     dash.dependencies.State('Price_MAX_Rent', 'value'),
     dash.dependencies.State('m2_MIN_Rent', 'value'),
     dash.dependencies.State('m2_MAX_Rent', 'value')]
    )
    
def Rent_Price_Limiter( n_clicks, Price_MIN_Sell, Price_MAX_Sell, m2_MIN_Sell, m2_MAX_Sell, 
                       Price_MIN_Rent, Price_MAX_Rent, m2_MIN_Rent, m2_MAX_Rent):
    my_world = world_new()
    
    #Price
    lok_sell_limit = lok_sell[lok_sell["price"].between(Price_MIN_Sell, Price_MAX_Sell, inclusive=True)]
    lok_sell_limit = lok_sell_limit.reset_index(drop=True)
    # print(lok_sell_limit)

    lok_rent_limit = lok_rent[lok_rent["rent_price"].between(Price_MIN_Rent, Price_MAX_Rent, inclusive=True)]
    lok_rent_limit = lok_rent_limit.reset_index(drop=True)
    
    #m2
    lok_sell_limit = lok_sell_limit[lok_sell_limit["m2"].between(m2_MIN_Sell, m2_MAX_Sell, inclusive=True)]
    lok_sell_limit = lok_sell_limit.reset_index(drop=True)
    
    lok_rent_limit = lok_rent_limit[lok_rent_limit["m2"].between(m2_MIN_Rent, m2_MAX_Rent, inclusive=True)]
    lok_rent_limit = lok_rent_limit.reset_index(drop=True)
    
    for row in range(len(lok_sell_limit.index)):
        folium.CircleMarker(
            location=[lok_sell_limit.at[row,'latitude'], lok_sell_limit.at[row,'longitude']],
            radius=3,
            popup='Sell price: ' + str(lok_sell_limit.at[row,'price']),
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=1
        ).add_to(my_world)
    
    for row in range(len(lok_rent_limit.index)):
        folium.CircleMarker(
            location=[lok_rent_limit.at[row,'latitude'], lok_rent_limit.at[row,'longitude']],
            radius=3,
            popup='Rent price: '+ str(lok_rent_limit.at[row,'rent_price']),
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=1
        ).add_to(my_world)
        
    total_rows_rent = len(lok_rent_limit.index) 
    total_rows_sell = len(lok_sell_limit.index) 
    
    html_string = my_world.get_root().render()
    
    fig = px.pie(values=[total_rows_sell, total_rows_rent],names=['Sell','Rent'])
    
    return html_string, total_rows_sell, total_rows_rent ,fig

@app.callback(
    [dash.dependencies.Output('Price_MIN_Sell', 'value'),
     dash.dependencies.Output('Price_MAX_Sell', 'value')],
    [dash.dependencies.Input('full-button_price_sell', 'n_clicks')]
    )

def give_full_price_sell(n_clicks_price_sell):     
    return min_value_sell_price, max_value_sell_price

@app.callback(
    [dash.dependencies.Output('m2_MIN_Sell', 'value'),
     dash.dependencies.Output('m2_MAX_Sell', 'value')],
    [dash.dependencies.Input('full-button_m2_sell', 'n_clicks')]
    )

def give_full_m2_sell(n_clicks_m2_sell):
    return min_value_sell_m2, max_value_sell_m2

@app.callback(
    [dash.dependencies.Output('Price_MIN_Rent', 'value'),
     dash.dependencies.Output('Price_MAX_Rent', 'value')],
    [dash.dependencies.Input('full-button_price_rent', 'n_clicks')]
    )

def give_full_price_rent(n_clicks_price_rent):
    return min_value_rent_price, max_value_rent_price

@app.callback(
    [dash.dependencies.Output('m2_MIN_Rent', 'value'),
     dash.dependencies.Output('m2_MAX_Rent', 'value')],
    [dash.dependencies.Input('full-button_m2_rent', 'n_clicks')]
    )

def give_full_m2_rent(n_clicks_m2_rent):
    return min_value_rent_m2, max_value_rent_m2

if __name__ == '__main__':
    # app.run_server(host='0.0.0.0', port=8050)
    serve(app.server, host='0.0.0.0', port=8050) # PRODUCTION