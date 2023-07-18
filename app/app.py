#Plotly Dash related imports
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State, no_update, callback_context, CeleryManager
from trace_updater import TraceUpdater
import plotly.graph_objects as go
from plotly_resampler import FigureResampler
from dash_extensions.enrich import (
    DashProxy,
    Serverside,
    ServersideOutputTransform,
    RedisBackend
)
import plotly.express as px

#cache and worker related imports
from flask_caching import Cache
import redis
from celery import Celery

#component imports from other files
import seismic, weather, gps, elementstyling, gpsvis
import calculations

#Obspy (seismic data processing library) imports 
from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client

#Environment variables related imports
import os, ast
from dotenv import load_dotenv

#Pyowm (library to pull weather data from OpenWeatherMap API)
from pyowm.owm import OWM

# Miscellaneous imports
import time
import pandas as pd
from datetime import date, timedelta, datetime

#database imports 
import sqlite3

import flask

load_dotenv() ## loads variables from environment file

### basic definitions and set up
redis_host = os.environ['CACHE_REDIS_HOST']
server = flask.Flask(__name__)
app = DashProxy(__name__, server = server, transforms=[ServersideOutputTransform(backends=[RedisBackend(host = redis_host)])], external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)


## creates redis cache with configuration described in .env file
cache = Cache(server, config={
    'CACHE_TYPE':os.environ['CACHE_TYPE'],
    'CACHE_REDIS_HOST':os.environ['CACHE_REDIS_HOST'],
    'CACHE_REDIS_PORT':os.environ['CACHE_REDIS_PORT'],
    'CACHE_REDIS_DB':os.environ['CACHE_REDIS_DB'],
    'CACHE_REDIS_URL':os.environ['CACHE_REDIS_URL'],
})

## Global variables
stations = ast.literal_eval(os.environ["SEISMIC_STATIONS"])

#create list of stations from "stations" dict
stationsoptions = list(stations.keys())

# weather coordinates and name from .env file
weather_coords = ast.literal_eval(os.environ["WEATHER_COORDS"])
weather_loc_name = os.environ["WEATHER_LOC_NAME"]


## Nav Bar
main_navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Seismic", href="/seismic")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Subheadings", header=True),
                dbc.DropdownMenuItem("East, North, & Up Movements", href="/gps"),
                dbc.DropdownMenuItem("Deformation Visualizations", href="/gpsdeform"),
            ],
            nav=True,
            in_navbar=True,
            label="Geodesy",
        ),
        dbc.NavItem(dbc.NavLink("Weather", href="/weather")),
        dbc.NavItem(dbc.NavLink("System Monitoring", href="/sysmon"))
    ],
    brand="MIT Haystack SGIP Data Monitor and Visualizer",
    color="primary",
    dark=True,
)

content = html.Div(id="page-content")

app.layout = html.Div([dcc.Location(id="url"), main_navbar, content, dcc.Store(id="storefigresamp"),
        TraceUpdater(id="trace-updater", gdID="waveformgraphgr"),])



### Redis Cache Methods ###

@cache.memoize(timeout=3600) ## refreshes hourly
def get_weather_data():
    print("fetching weather data...")
    weather_api_key = os.environ["OPEN_WEATHER_API_KEY"]
    owm = OWM(weather_api_key)
    mgr = owm.weather_manager()
    output = {}

    location = ast.literal_eval(os.environ["WEATHER_COORDS"]) ## gets location of where to find weather
    ross_ice_shelf_latitude = location[0]
    ross_ice_shelf_longitude = location[1]

    weather_ris = mgr.weather_at_coords(ross_ice_shelf_latitude, ross_ice_shelf_longitude).weather 

    '''
    Creating output dict that stores the following keys:
    - 'current temp': the current temperature
    - 'feels like': what the temperature feels like
    - 'wind speed': current wind speed
    - 'pressure': current pressure
    - 'icon': weather image
    - 'description': short description of current conditions
    '''
    temp_celsius = weather_ris.temperature('celsius')
    output['current temp'] = temp_celsius['temp']
    output['feels like'] = temp_celsius['feels_like']

    wind_dict_in_meters_per_sec = weather_ris.wind()
    output['wind speed'] = wind_dict_in_meters_per_sec['speed']

    weather_pressure = weather_ris.barometric_pressure()
    output['pressure'] = weather_pressure['press']

    output['icon'] = weather_ris.weather_icon_url(size='2x')

    output['description'] = weather_ris.detailed_status

    return output

@cache.memoize(timeout=21600) ## refreshes every 6 hours
def get_future_weather_data():
    print("fetching future weather data...")

    weather_api_key = os.environ["OPEN_WEATHER_API_KEY"]
    owm = OWM(weather_api_key)
    mgr = owm.weather_manager()
    output = {}

    location = ast.literal_eval(os.environ["WEATHER_COORDS"])
    ross_ice_shelf_latitude = location[0]
    ross_ice_shelf_longitude = location[1]

    ## fetches future forecast
    weather_ris = mgr.forecast_at_coords(ross_ice_shelf_latitude, ross_ice_shelf_longitude, '3h')

    '''
    Saves 4 days of future weather data in output dict. The keys are (where x represents either one, two, three, or four):
    - date_xday: the date of the forecast
    - img_xday: the image corresponding to the forecast prediction
    - description_xday: short description of weather conditions
    - temperature_xday: prediction of future temperature
    '''
    oneday = date.today() + timedelta(days = 1)
    weather_oneday = weather_ris.get_weather_at(datetime(oneday.year, oneday.month, oneday.day, 12, 0, 0)) 
    output['date_oneday'] = date.today() + timedelta(days = 1)
    output['img_oneday'] = weather_oneday.weather_icon_url(size='2x')
    output['description_oneday'] = weather_oneday.detailed_status
    output['temperature_oneday'] = weather_oneday.temperature('celsius')['temp']

    twoday = date.today() + timedelta(days = 2)
    weather_twoday = weather_ris.get_weather_at(datetime(twoday.year, twoday.month, twoday.day, 12, 0, 0)) 
    output['date_twoday'] = date.today() + timedelta(days = 2)
    output['img_twoday'] = weather_twoday.weather_icon_url(size='2x')
    output['description_twoday'] = weather_twoday.detailed_status
    output['temperature_twoday'] = weather_twoday.temperature('celsius')['temp']

    threeday = date.today() + timedelta(days = 3)
    weather_threeday = weather_ris.get_weather_at(datetime(threeday.year, threeday.month, threeday.day, 12, 0, 0)) 
    output['date_threeday'] = date.today() + timedelta(days = 3)
    output['img_threeday'] = weather_threeday.weather_icon_url(size='2x')
    output['description_threeday'] = weather_threeday.detailed_status
    output['temperature_threeday'] = weather_threeday.temperature('celsius')['temp']

    fourday = date.today() + timedelta(days = 4)
    weather_fourday = weather_ris.get_weather_at(datetime(fourday.year, fourday.month, fourday.day, 12, 0, 0)) 
    output['date_fourday'] = date.today() + timedelta(days = 4)
    output['img_fourday'] = weather_fourday.weather_icon_url(size='2x')
    output['description_fourday'] = weather_fourday.detailed_status
    output['temperature_fourday'] = weather_fourday.temperature('celsius')['temp']

    return output

#@cache.memoize(timeout=21600) # refreshes every 6 hours
def create_gps_five_days():
    ## attempts to pull gps data from past 5 days from the database
    starttime = str(date.today() - timedelta(days=365))[:10]
    endtime = str(date.today() - timedelta(days=360))[:10]

    #starttime = str(date.today())[:10]
    #endtime = str(date.today() - timedelta(days=5))[:10]

    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()

    query = f"""SELECT timestamp, eastingsf, northingsf, verticalf, station
    FROM gps_data WHERE timestamp >= ? AND timestamp <= ?; """
    query_inputs  = (starttime, endtime)
    cur.execute(query, query_inputs)
    all_results = cur.fetchall()

    if not all_results:
        return dbc.Label("No data was found."), dbc.Label("No data was found."), dbc.Label("No data was found.")
    
    ## creating dataframe with all data
    times, east, north, up, stations = [], [], [], [], []
    for res in all_results:
        times.append(res[0])
        east.append(res[1])
        north.append(res[2])
        up.append(res[3])
        stations.append(res[4])

    df = pd.DataFrame({
        'Date': times,
        'East (m)': east, 
        'North (m)': north, 
        'Up (m)': up, 
        'Station': stations
    })

    ## creating 3 figures for all 3 locations
    fig_east = px.line(df, x="Date", y="East (m)", color="Station")
    fig_north = px.line(df, x="Date", y="North (m)", color="Station")
    fig_up = px.line(df, x="Date", y="Up (m)", color="Station")

    fig_east.update_layout(template='plotly_dark')
    fig_north.update_layout(template='plotly_dark')
    fig_up.update_layout(template='plotly_dark')

    conn.close()
    return dcc.Graph(figure = fig_east), dcc.Graph(figure = fig_north), dcc.Graph(figure = fig_up)


### Home Page Components ###

# Weather Section

weather_title = html.H5("Weather", style = elementstyling.MARGIN_STYLE)

def get_current_weather():
    ## creates current weather component
    allweatherdict = get_weather_data()
    current_weather_left_side = dbc.Col([html.H2(weather_loc_name), f"""Latitude: {weather_coords[0]}, Longitude: {weather_coords[1]} """, html.Br(),
                                       ], width = 6,  style={"text-align": "center"})
    current_weather_right_side = dbc.Col([f"""Current Temperature: {allweatherdict["current temp"]} C""", html.Br(),
                                         f"""Feels like: {allweatherdict["feels like"]} C""", html.Br(),
                                      f"""Wind Speed: {allweatherdict["wind speed"]} m/s""", html.Br(), f"""Pressure: {allweatherdict["pressure"]} hPa"""], width = 6, style={"text-align": "center"})
    return  dbc.Card([dbc.Row([current_weather_left_side, current_weather_right_side])],  body=True, style=elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)


def get_weather_predictions():
    # creates future weather predictions component
    allweatherdict = get_future_weather_data()
    weather_oneday = dbc.Card([allweatherdict["date_oneday"],  html.Br(), html.Img(src=allweatherdict["img_oneday"]), html.Br(),
                               allweatherdict["description_oneday"], html.Br(), f"""{allweatherdict["temperature_oneday"]} C"""], body = True)
    weather_twoday = dbc.Card([allweatherdict["date_twoday"], html.Br(), html.Img(src=allweatherdict["img_twoday"]), html.Br(),
                               allweatherdict["description_twoday"], html.Br(), f"""{allweatherdict["temperature_twoday"]} C"""], body = True)
    weather_threeday = dbc.Card([allweatherdict["date_threeday"], html.Br(), html.Img(src=allweatherdict["img_threeday"]), html.Br(),
                               allweatherdict["description_threeday"], html.Br(), f"""{allweatherdict["temperature_threeday"]} C"""], body = True)
    weather_fourday = dbc.Card([allweatherdict["date_fourday"], html.Br(), html.Img(src=allweatherdict["img_fourday"]), html.Br(),
                               allweatherdict["description_fourday"], html.Br(), f"""{allweatherdict["temperature_fourday"]} C"""], body = True)
    return dbc.Card([dbc.Row([dbc.Col(weather_oneday, style={"text-align": "center"}), dbc.Col(weather_twoday, style={"text-align": "center"}),
                                          dbc.Col(weather_threeday, style={"text-align": "center"}),dbc.Col(weather_fourday, style={"text-align": "center"}),
                                          ])],  body=True, style=elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)

def get_weather_row():
    return dbc.Row([dbc.Col([get_current_weather()], width = 5), dbc.Col([get_weather_predictions()], width = 7)])
   
# File Download Section

file_download_title = html.H5("Recently Downloaded Files", style = elementstyling.MARGIN_STYLE)

def get_log_tables():
    seismic_log_table = calculations.read_file("logs/seismic_log.txt")
    seismic_data_downloads = dbc.Card(["Seismic Data", html.Br(),html.Br(), seismic_log_table],  body=True, style = elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

    gps_log_table = calculations.read_file("logs/gps_log.txt")
    gps_data_downloads = dbc.Card(["GPS Data Download Table", html.Br(),html.Br(), gps_log_table],  body=True, style = elementstyling.CARD_HALF_WIDTH_DOWNUP)

    weather_log_table = calculations.read_file("logs/weather_log.txt", "weather")
    weather_data_downloads = dbc.Card(["Weather Data Download Table", html.Br(),html.Br(), weather_log_table],  body=True, style = elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)

    return dbc.Row([dbc.Col(seismic_data_downloads, width = 4), dbc.Col(gps_data_downloads, width = 3), dbc.Col(weather_data_downloads, width = 5)])

# Seismic Data Section

seismic_data_title = html.H5("Seismic Data", style = elementstyling.MARGIN_STYLE)

#Dropdown to choose seismic station for spectrogram
home_dropdown_seismic_station_spec = html.Div(
    [
        dbc.Label("Select seismic station:"),
        dcc.Dropdown(
            stationsoptions,
            stationsoptions[0],
            id="dropdownhomeseisspec",
            clearable=False,
        ),
    ],
)

#Dropdown to choose seismic station for psd
home_dropdown_seismic_station_psd = html.Div(
    [
        dbc.Label("Select seismic station:"),
        dcc.Dropdown(
            stationsoptions,
            stationsoptions[0],
            id="dropdownhomeseispsd",
            clearable=False,
        ),
    ],
)

seismic_summary_spectrogram = dbc.Card(["Summary Spectrogram", html.Br(), html.Br(), home_dropdown_seismic_station_spec, html.Br(), dbc.Spinner(html.Div(id = "summaryspec"), color = "primary")],  body=True, style = elementstyling.CARD_HALF_WIDTH_LEFT)

seismic_summary_psd = dbc.Card(["Summary PSD", html.Br(), html.Br(), home_dropdown_seismic_station_psd, html.Br(), dbc.Spinner(html.Div(id = "summarypsd"), color="primary")],  body=True, style = elementstyling.CARD_HALF_WIDTH_RIGHT)

all_seismic_row = dbc.Row([dbc.Col(seismic_summary_spectrogram), dbc.Col(seismic_summary_psd)])

# GPS Data Section

gps_data_title = html.H5("GPS Data", style = elementstyling.MARGIN_STYLE)

gps_summary_movement =  dbc.Card("GPS Summer Movement (over 5 days)",  body=True, style=elementstyling.MARGIN_STYLE)

def get_gps_tables():
    east_g, north_g, up_g = create_gps_five_days()

    east_graph = dbc.Card(["East Movement", html.Br(),html.Br(), html.Div(children = east_g)],  body=True, style = elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

    north_graph = dbc.Card(["North Movement", html.Br(),html.Br(), html.Div(children = north_g)],  body=True, style = elementstyling.CARD_HALF_WIDTH_DOWNUP)

    up_graph = dbc.Card(["Up Movement", html.Br(),html.Br(), html.Div(children = up_g)],  body=True, style = elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)

    return dbc.Row([dbc.Col(east_graph, width = 4), dbc.Col(north_graph, width = 4), dbc.Col(up_graph, width = 4)])


## Method to get all elements of home page
def get_all_home_elements():
    return [weather_title, get_weather_row(),
                         file_download_title, get_log_tables(), 
                         seismic_data_title, all_seismic_row, 
                         gps_data_title, get_gps_tables()]




### ALL CALLBACKS ###

# Seismic Page Callbacks

#callback to update waveform, spectrogram, and PSD
@app.callback(
        Output("storefigresamp", "data"),
        Output("waveformgraph", "children"), 
        Output("spectrogramgraph", "children"), 
        Output("psdgraph", "children"),
        Input("formsubmitbut", "n_clicks"),
        State("storefigresamp", "data"),
        State("dropdownseismic", "value"), 
        State("timeframepicker", "start_date"),
        State("timeframepicker", "end_date"),
        State("dropdownwavefilt", "value"), 
        memoize=True,
)
def update_seismic_page(submitted, fig, station, start_date, end_date, wavefilt):
    ctx = callback_context
    if len(ctx.triggered) and "formsubmitbut" in ctx.triggered[0]["prop_id"]:
        if fig is None:
            fig: FigureResampler = FigureResampler(go.Figure())
        else:
            fig.replace(go.Figure())
        start = time.time()
        waveform_graph, waveform, inventory = calculations.create_waveform_graph(stations[station]["net"], station, stations[station]["chan"], start_date, end_date,
                                        wavefilt, fig)
        spectrogram = calculations.create_spectrogram(waveform)
        psd = calculations.create_psd(waveform, inventory)
        print(time.time() - start, flush = True)

    return [Serverside(fig), waveform_graph, spectrogram, psd]

# Weather Page Callbacks

#callback to update temperature, pressure, & humidity graph
@app.callback(
    Output("weather_temp_graph", "children"),
    Output("weather_pressure_graph", "children"), 
    Output("weather_humidity_graph", "children"),
    State("weather_datepicker", "start_date"),
    State("weather_datepicker", "end_date"),
    Input("weather_formsubmitbut", "n_clicks")
)
def update_weather_content(start_date, end_date, n_clicks):
    return calculations.create_weather_graphs(start_date, end_date)

#GPS Page Callbacks

# Callback to update East, North, & Upwards Movement
@app.callback(
    Output("gps_east_graph", "children"),
    Output("gps_north_graph", "children"), 
    Output("gps_up_graph", "children"),
    State("gps_datepicker", "start_date"),
    State("gps_datepicker", "end_date"),
    State("gps_dropdown", "value"),
    Input("gps_formsubmitbut", "n_clicks")
)
def update_gps_content(start_date, end_date, station, n_clicks):
    return calculations.create_gps_graphs(start_date, end_date, station)

# GPS Vis Page Callbacks

# callback to update animation
@app.callback(
        Output("gps_animation", "children"), 
        State("gps_vis_dropdown", "value"), 
        State("gps_vis_datepicker", "start_date"), 
        State("gps_vis_datepicker", "end_date"), 
        Input("gpsvis_formsubmitbut", "n_clicks")
)
def update_gps_vis_content(station, start_date, end_date, n_clicks):
    return calculations.get_gps_loc(start_date, end_date, station)

# Callback to update distance/orientation graphs
@app.callback(
        Output("baseline_length", "children"), 
        Output("baseline_orient", "children"), 
        Output("baseline_length_resid", "children"), 
        Output("baseline_orient_resid", "children"), 
        State("gps_vis_dropdown2", "value"),
        State("gps_vis_datepicker2", "start_date"), 
        State("gps_vis_datepicker2", "end_date"), 
        Input("gpsvis_formsubmitbut2", "n_clicks")
)
def update_gps_vis_disori_content(refstation, start_date, end_date, n_clicks):
    return calculations.get_baseline_graphs(start_date, end_date, refstation)

# Home Page Callbacks

# Callback to update summary spectrogram
@app.callback(
        Output("summaryspec", "children"), 
        Input("dropdownhomeseisspec", "value")
)
def update_spec_home_page(station):
    return calculations.create_spec_five_days(station)

# Callback to update summary PSD
@app.callback(
        Output("summarypsd", "children"), 
        Input("dropdownhomeseispsd", "value")
)
def update_spec_home_page(station):
    return calculations.create_psd_five_days(station)


## callback to detrmine page content
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        all_home_elements = get_all_home_elements()
        return html.Div(all_home_elements)
    elif pathname == "/seismic":
        return html.Div(seismic.ALL_SEISMIC_ELEMENTS)
    elif pathname == "/weather":
        return html.Div(weather.get_all_weather_elements())
    elif pathname == "/gps":
        return html.Div(gps.get_all_gps_elements())
    elif pathname =="/gpsdeform":
        return html.Div(gpsvis.get_all_gpsvis_elements())
    elif pathname == "/sysmon":
        return html.P("Oh cool, this is the system monitoring page!")
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

## Callback for Plotly Resampler (used for seismic waveform graph)
@app.callback(
    Output("trace-updater", "updateData"),
    Input("waveformgraphgr", "relayoutData"),
    State("storefigresamp", "data"),  # The server side cached FigureResampler per session
    prevent_initial_call=True,
    memoize=True,
)
def update_fig(relayoutdata, fig):
    if fig is None:
        return no_update
    return fig.construct_update_data(relayoutdata)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)