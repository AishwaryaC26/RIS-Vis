#Plotly Dash related imports
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State, no_update, callback_context, ctx
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

#component imports from other files
import seismic, weather, gps, elementstyling, gpsvis, monvct, monph, monga, monu
import calculations, componentbuilder

#Environment variables related imports
import os, ast
from dotenv import load_dotenv

#Pyowm (library to pull weather data from OpenWeatherMap API)
from pyowm.owm import OWM

# Miscellaneous imports
import time
import pandas as pd
from datetime import date, timedelta, datetime
import math
import flask

load_dotenv() ## loads variables from environment file

### basic definitions and set up
redis_host = os.environ['CACHE_REDIS_HOST']
server = flask.Flask(__name__)
app = DashProxy(__name__, server = server, transforms=[ServersideOutputTransform(backends=[RedisBackend(host = redis_host)])], external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True)
app.title = 'RIS-Vis'
app.favicon = "assets/favicon.ico"

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
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Subheadings", header=True),
                dbc.DropdownMenuItem("Voltage, Current, & Temperature", href="/monvct"),
                dbc.DropdownMenuItem("Pressure & Humidity", href="/monph"),
                dbc.DropdownMenuItem("Gyroscope & Accelerometer", href="/monga"),
                dbc.DropdownMenuItem("Utility", href="/monu"),
            ],
            nav=True,
            in_navbar=True,
            label="System Monitoring",
        ),
    ],
    brand="RIS-Vis: MIT Haystack SGIP Data Monitor and Visualizer",
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
    ross_ice_shelf_latitude = location[0][1]
    ross_ice_shelf_longitude = location[0][2]

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
    ross_ice_shelf_latitude = location[0][1]
    ross_ice_shelf_longitude = location[0][2]

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


## creates spectrograms for past 3 days given list of stations
@cache.memoize(timeout=21600) ##refreshes every 6 hours
def create_spec_three_days(stations):
    figs = []
    for station in stations:
        starttime = str(date.today() - timedelta(days=365))[:10]
        endtime = str(date.today() - timedelta(days=360))[:10]

        #starttime = str(date.today() - timedelta(days=3))[:10]
        #endtime = str(date.today())[:10]
        
        all_results = calculations.check_database(station, starttime, endtime)
        if not all_results:
            figs.append(dbc.Label("No data was found"))
            continue
        stream = calculations.create_stream(all_results)
        if not stream:
            figs.append(dbc.Label("No data was found"))
            continue
        figs.append(calculations.create_spectrogram(stream))
    while len(figs) < 3:
        figs.append(None)
    return figs

### Home Page Components ###

# Weather Section

def get_current_weather():
    ## creates current weather component
    allweatherdict = get_weather_data()
    current_weather = html.Div([html.H2(weather_loc_name), f"""Latitude: {weather_coords[0][1]}, Longitude: {weather_coords[0][2]} """, html.Hr(), 
                                         f"""Current Temperature: {allweatherdict["current temp"]} C""", html.Br(),
                                         f"""Feels like: {allweatherdict["feels like"]} C""", html.Br(),
                                      f"""Wind Speed: {allweatherdict["wind speed"]} m/s""", html.Br(), f"""Pressure: {allweatherdict["pressure"]} hPa"""], style={"text-align": "center"})
    return  dbc.Card([current_weather],  body=True,)


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
    return dbc.Row([dbc.Col(weather_oneday, style={"text-align": "center"}), dbc.Col(weather_twoday, style={"text-align": "center"}),
                                          dbc.Col(weather_threeday, style={"text-align": "center"}),dbc.Col(weather_fourday, style={"text-align": "center"}),
                                          ])

## creates map component with weather location used in OpenWeatherMap API
def get_map_component():
    location= weather_coords
    df = pd.DataFrame(location, columns=['Station', 'Latitude', 'Longitude'])

    fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", zoom=1, height=245)
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            }
        ])
    fig.update_traces(marker=dict(
        size = 20
    ),)
    fig.update_layout(
    margin=dict(l=5,r=5,b=5,t=20),
    )
    fig.update_layout(template='plotly_dark')
    return dcc.Graph(figure = fig)


## creates full weather row for home page
def get_weather_row(card_desc):
    weather_row = dbc.Row([dbc.Col([get_current_weather()], width = 3), dbc.Col([get_map_component()], width = 3), dbc.Col([get_weather_predictions()], width = 6)])
    weather_component = html.Div([html.Br(), dbc.Row([dbc.Col(html.H4("Weather Data", className="card-title"), width = 6), 
            dbc.Col(html.Div([ dbc.Button(html.I(className="fas fa-question", style={'fontSize': '30px'}), id="weather-q-id", n_clicks=0, style =  elementstyling.IMG_STYLING),], style = {"float": "right"}), width = 6)]),
            dbc.Modal(
                [
                dbc.ModalHeader([html.H4("Description", className="card-title")]),
                dbc.ModalBody(card_desc)
                ],
                id="weather-q-modal-id",
                is_open=False,
                size="xl",
                keyboard=False,
                backdrop="static",
            ),
        dbc.Spinner([html.Div([weather_row])], color="primary"), 
        html.Br(), ], style=None)
    return weather_component
   
weather_desc = "The weather data/predictions being used in the SGIP Dashboard are from the OpenWeatherMap API. Data is updated hourly." ## description for what should be displayed in weather-information modal

# File Download Section

log_desc = "Log tables show the last 200 files that have been downloaded with respect to seismic data, GPS data, and weather data." ## description for what should be displayed in log-information modal


'''
Returns  Card component with 3 tables (seismic, GPS, weather) with names and dates of files downloaded
'''
def get_log_tables(card_desc):
    seismic_log_table = calculations.read_file("logs/seismic_log.txt")
    seismic_data_downloads = dbc.Card([html.H4("Seismic Data Download Table"), html.Br(), seismic_log_table],  body=True)

    gps_log_table = calculations.read_file("logs/gps_log.txt")
    gps_data_downloads = dbc.Card([html.H4("GPS Data Download Table"), html.Br(), gps_log_table],  body=True)

    weather_log_table = calculations.read_file("logs/weather_log.txt", "weather")
    weather_data_downloads = dbc.Card([html.H4("Weather Data Download Table"), html.Br(), weather_log_table],  body=True)

    log_components =  dbc.Row([dbc.Col(seismic_data_downloads, width = 4), dbc.Col(gps_data_downloads, width = 3), dbc.Col(weather_data_downloads, width = 5)])

    full_card = html.Div([dbc.Row([dbc.Col(html.H4("Recently Downloaded Files", className="card-title"), width = 6), 
            dbc.Col(html.Div([ dbc.Button(html.I(className="fas fa-question", style={'fontSize': '30px'}), id="log-q-id", n_clicks=0, style =  elementstyling.IMG_STYLING),], style = {"float": "right"}), width = 6)]),
            dbc.Modal(
                [
                dbc.ModalHeader([html.H4("Description", className="card-title")]),
                dbc.ModalBody(card_desc)
                ],
                id="log-q-modal-id",
                is_open=False,
                size="xl",
                keyboard=False,
                backdrop="static",
            ),
        dbc.Spinner([html.Div([log_components])], color="primary"), ], style=None)
    return full_card

# Seismic Data Section

spec_desc = "These graphs display summary spectrograms for the last 5 days. Data is updated every 6 hours." ##description for seismic information modal component

## builds component to display summary spectrograms for all seismic stations
def build_summaryspec_component(card_desc):
    num_pages = math.ceil(len(stationsoptions) / 3)
    #card_title_id, open_expand_button_id, close_expand_button_id, modal_body_id, modal_id, graph_div_id, full_card_id, element_styling = None
    card_1 = componentbuilder.build_graph_component_noq("sumspec-card1-titleid", "sumspec-card1-expand-button-id", "sumspec-card1-close-button-id", 
                                                        "sumspec-card1-modalbody-id", "sumspec-card1-modal-id", 
                                                        "sumspec1", "sumspec-card1-id", None)
    card_2 = componentbuilder.build_graph_component_noq("sumspec-card2-titleid", "sumspec-card2-expand-button-id", "sumspec-card2-close-button-id", 
                                                        "sumspec-card2-modalbody-id", "sumspec-card2-modal-id", 
                                                        "sumspec2", "sumspec-card2-id", None)
    card_3 = componentbuilder.build_graph_component_noq("sumspec-card3-titleid", "sumspec-card3-expand-button-id", "sumspec-card3-close-button-id", 
                                                        "sumspec-card3-modalbody-id", "sumspec-card3-modal-id", 
                                                        "sumspec3", "sumspec-card3-id", None)

    graphs_card = dbc.Row([dbc.Col(card_1, width = 4), dbc.Col(html.Div(card_2), width = 4), dbc.Col(html.Div(card_3), width = 4)])
    data_graph = html.Div([dbc.Row([dbc.Col(html.H4("Summary Spectrograms", className="card-title"), width = 6), 
            dbc.Col(html.Div([ dbc.Button(html.I(className="fas fa-question", style={'fontSize': '30px'}), id="specsum-q-id", n_clicks=0, style =  elementstyling.IMG_STYLING),], style = {"float": "right"}), width = 6)]),
            dbc.Modal(
                [
                dbc.ModalHeader([html.H4("Description", className="card-title")]),
                dbc.ModalBody(card_desc)
                ],
                id="specsum-q-modal-id",
                is_open=False,
                size="xl",
                keyboard=False,
                backdrop="static",
            ),
        dbc.Spinner([html.Div([graphs_card])], color="primary"), 
        html.Br(), 
        html.H6("Slider",),
        dcc.Slider(min=1, max=num_pages, step=1, value=1, id="specsumslider")], style=None)
    return data_graph


## Method to get all elements of home page
def get_all_home_elements():
    return [get_weather_row(weather_desc), build_summaryspec_component(spec_desc), get_log_tables(log_desc),]


### ALL CALLBACKS ###

# Seismic Page Callbacks

#callback to update waveform, spectrogram, and PSD
@app.callback(
        Output("storefigresamp", "data"),
        Output("waveformgraph", "children", allow_duplicate=True), 
        Output("spectrogramgraph", "children"), 
        Output("psdgraph", "children"),
        Input("formsubmitbut", "n_clicks"),
        State("storefigresamp", "data"),
        State("dropdownseismic", "value"), 
        State("timeframepicker", "start_date"),
        State("timeframepicker", "end_date"),
        State("dropdownwavefilt", "value"), 
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

# callback to create GPS tracks
@app.callback(
        Output("gps_animation", "figure"), 
        State("gps_vis_datepicker", "start_date"), 
        State("gps_vis_datepicker", "end_date"), 
        Input("gpsvis_formsubmitbut", "n_clicks")
)
def update_gps_vis_content(start_date, end_date, n_clicks):
    return calculations.get_gps_tracks(start_date, end_date)

# Callback to update distance/orientation graphs
@app.callback(
        Output("baseline_length", "children"), 
        Output("baseline_orient", "children"), 
        Output("baseline_length_resid", "children"), 
        Output("baseline_orient_resid", "children"), 
        Output("gps_animation2", "children"),
        State("gps_vis_dropdown2", "value"),
        State("gps_vis_datepicker2", "start_date"), 
        State("gps_vis_datepicker2", "end_date"), 
        Input("gpsvis_formsubmitbut2", "n_clicks")
)
def update_gps_vis_disori_content(refstation, start_date, end_date, n_clicks):
    return calculations.get_baseline_graphs(start_date, end_date, refstation)

##callback to zoom in on point on GPS Tracks MapBox whenever it is clicked
@app.callback(
    Output('gps_animation', 'figure', allow_duplicate=True),
    State('gps_animation', 'figure'),
    Input('gps_animation', 'clickData'),
    prevent_initial_call = True)
def update_y_timeseries(currFigure, clickData):
    lat_foc = clickData['points'][0]['lat']
    lon_foc = clickData['points'][0]['lon']
    currFigure['layout']['mapbox']['center'] = {'lat': lat_foc, 'lon': lon_foc}
    currFigure['layout']['mapbox']['zoom'] = 40
    return currFigure


## System Monitoring Page Callbacks

#CPU, Memory, & Disk space Callback
@app.callback(
        Output("cu_graph", "children"), 
        Output("mu_graph", "children"), 
        Output("fu_graph", "children"), 
        State("u_datepicker", "start_date"), 
        State("u_datepicker", "end_date"), 
        Input("monu_formsubmitbut", "n_clicks")
)
def update_sysmon(start, end, n_clicks):
    return calculations.get_cmd(start, end)

# Monitoring Voltage, Current, Temp. Callbacks
@app.callback(
        Output("v2b_graph", "children"), 
        Output("vFb_graph", "children"), 
        Output("c2b_graph", "children"), 
        Output("cFb_graph", "children"), 
        Output("tIb_graph", "children"), 
        State("monvct_datepicker", "start_date"), 
        State("monvct_datepicker", "end_date"), 
        Input("monvct_formsubmitbut", "n_clicks")
)
def update_sysmon(start, end, n_clicks):
    return calculations.get_vct(start, end)

#Pressure, Humidity inside Box callback
@app.callback(
        Output("pIb_graph", "children"), 
        Output("hIb_graph", "children"), 
        State("ph_datepicker", "start_date"), 
        State("ph_datepicker", "end_date"), 
        Input("monph_formsubmitbut", "n_clicks")
)
def update_sysmon(start, end, n_clicks):
    return calculations.get_ph(start, end)

#Gyroscope and Acceleration callback
@app.callback(
        Output("gx_graph", "children"), 
        Output("gy_graph", "children"), 
        Output("gz_graph", "children"), 
        Output("ax_graph", "children"), 
        Output("ay_graph", "children"), 
        Output("az_graph", "children"), 
        State("monga_datepicker", "start_date"), 
        State("monga_datepicker", "end_date"), 
        Input("monga_formsubmitbut", "n_clicks")
)
def update_sysmon(start, end, n_clicks):
    return calculations.get_ga(start, end)

# Home Page Callbacks

# Callback to update summary spectrogram
@app.callback( 
        Output("sumspec1", "children"),
        Output("sumspec2", "children"), 
        Output("sumspec3", "children"),
        Output("sumspec-card1-titleid", "children"), 
        Output("sumspec-card2-titleid", "children"),
        Output("sumspec-card3-titleid", "children"),
        Output("sumspec-card1-id", "style"), 
        Output("sumspec-card2-id", "style"), 
        Output("sumspec-card3-id", "style"), 
        Input("specsumslider", "value")
)
def update_summary_spectrogram(slider_val):
    start = slider_val - 1
    used_stations = stationsoptions[start * 3:start * 3 + 3]
    titles = [f"""Station: {st}""" for st in used_stations]
    while len(titles) < 3:
        titles.append("")
    graphs = create_spec_three_days(used_stations)
    check1 = {'display':'none'} if not titles[0] else {}
    check2 = {'display':'none'} if not titles[1] else {}
    check3 = {'display':'none'} if not titles[2] else {}
    return graphs[0], graphs[1], graphs[2], titles[0], titles[1], titles[2], check1, check2, check3


## Callbacks to handle opening and closing of Description Modals (the question button)
@app.callback( 
        Output("monuq-modal", "is_open"), 
        Input("open-monuq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback( 
        Output("mongaq-modal", "is_open"), 
        Input("open-mongaq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback( 
        Output("monphq-modal", "is_open"), 
        Input("open-monphq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback( 
        Output("monvctq-modal", "is_open"), 
        Input("open-monvctq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("cu-q-modal", "is_open"), 
        Input("open-cu-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("mu-q-modal", "is_open"), 
        Input("open-mu-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("fu-q-modal", "is_open"), 
        Input("open-fu-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True


@app.callback(
        Output("gx-q-modal", "is_open"), 
        Input("open-gx-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gy-q-modal", "is_open"), 
        Input("open-gy-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gz-q-modal", "is_open"), 
        Input("open-gz-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("ax-q-modal", "is_open"), 
        Input("open-ax-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("ay-q-modal", "is_open"), 
        Input("open-ay-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("az-q-modal", "is_open"), 
        Input("open-az-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("hIb-q-modal", "is_open"), 
        Input("open-hIb-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("pIb-q-modal", "is_open"), 
        Input("open-pIb-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("v2b-q-modal", "is_open"), 
        Input("open-v2b-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("vFb-q-modal", "is_open"), 
        Input("open-vFb-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("c2b-q-modal", "is_open"), 
        Input("open-c2b-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("cFb-q-modal", "is_open"), 
        Input("open-cFb-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True


@app.callback(
        Output("tIb-q-modal", "is_open"), 
        Input("open-tIb-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("waveformq-modal", "is_open"), 
        Input("open-waveformq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("specq-modal", "is_open"), 
        Input("open-specq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("psdq-modal", "is_open"), 
        Input("open-psdq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gps-east-q-modal", "is_open"), 
        Input("open-gps-east-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gps-north-q-modal", "is_open"), 
        Input("open-gps-north-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gps-up-q-modal", "is_open"), 
        Input("open-gps-up-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

## gpsvis
@app.callback(
        Output("gpsvis-ani-q-modal", "is_open"), 
        Input("open-gpsvis-ani-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsvis-ani2-q-modal", "is_open"), 
        Input("open-gpsvis-ani2-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsvis-base-q-modal", "is_open"), 
        Input("open-gpsvis-base-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsvis-orient-q-modal", "is_open"), 
        Input("open-gpsvis-orient-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsvis-lengthres-q-modal", "is_open"), 
        Input("open-gpsvis-lengthres-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsvis-orientres-q-modal", "is_open"), 
        Input("open-gpsvis-orientres-q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("weather-temp-q-modal", "is_open"), 
        Input("open-weather-tempq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("weather-press-q-modal", "is_open"), 
        Input("open-weather-pressq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("weather-hum-q-modal", "is_open"), 
        Input("open-weather-humq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("specsum-q-modal-id", "is_open"), 
        Input("specsum-q-id", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("weather-q-modal-id", "is_open"), 
        Input("weather-q-id", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("log-q-modal-id", "is_open"), 
        Input("log-q-id", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("seismicq-modal", "is_open"), 
        Input("open-seismicq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsq-modal", "is_open"), 
        Input("open-gpsq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsvis1-q-modal", "is_open"), 
        Input("open-gpsvis1q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("gpsvis2-q-modal", "is_open"), 
        Input("open-gpsvis2q-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True

@app.callback(
        Output("weather-q-modal", "is_open"), 
        Input("open-weatherq-button", "n_clicks"), 
        prevent_initial_call=True,
)
def open_description(n_clicks):
    return True


## Callbacks to handle opening and closing of Expand Modals

## method to make sure overall range of graph stays the same in expansio modal
def update_axis_ranges(graph):
    if graph and "figure" in graph["props"] and "layout" in graph["props"]["figure"] and "xaxis" in graph["props"]["figure"]["layout"] and "yaxis" in graph["props"]["figure"]["layout"]:
        graph["props"]["figure"]["layout"]["xaxis"]["autorange"] = True
        graph["props"]["figure"]["layout"]["yaxis"]["autorange"] = True

## method to handle expansion of modals 
def update_expand(ctx, open_button_id, close_button_id, modal_open, modal_graph, page_graph):
    which_inp = ctx.triggered_id if not None else 'No clicks yet'
    if which_inp == open_button_id:
        if modal_open: 
            update_axis_ranges(modal_graph)
            return modal_graph, True, None
        else:
            update_axis_ranges(page_graph) 
            return page_graph, True, None
    elif which_inp == close_button_id:
        if modal_open:
            update_axis_ranges(modal_graph)
            return None, False, modal_graph
        else: ## should never happen but just in case
            update_axis_ranges(page_graph)
            return None, False, page_graph
    else:
        return no_update
    
@app.callback(
    Output("cu-modal-body", "children"), 
    Output("cu-modal", "is_open"),
    Output("cu_graph", "children", allow_duplicate=True), 
    State("cu_graph", "children"), 
    State("cu-modal-body", "children"), 
    State("cu-modal", "is_open"),
    Input("open-cu-modal", "n_clicks"), 
    Input("close-cu-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-cu-modal", "close-cu-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("mu-modal-body", "children"), 
    Output("mu-modal", "is_open"),
    Output("mu_graph", "children", allow_duplicate=True), 
    State("mu_graph", "children"), 
    State("mu-modal-body", "children"), 
    State("mu-modal", "is_open"),
    Input("open-mu-modal", "n_clicks"), 
    Input("close-mu-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-mu-modal", "close-mu-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("fu-modal-body", "children"), 
    Output("fu-modal", "is_open"),
    Output("fu_graph", "children", allow_duplicate=True), 
    State("fu_graph", "children"), 
    State("fu-modal-body", "children"), 
    State("fu-modal", "is_open"),
    Input("open-fu-modal", "n_clicks"), 
    Input("close-fu-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-fu-modal", "close-fu-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("gx-modal-body", "children"), 
    Output("gx-modal", "is_open"),
    Output("gx_graph", "children", allow_duplicate=True), 
    State("gx_graph", "children"), 
    State("gx-modal-body", "children"), 
    State("gx-modal", "is_open"),
    Input("open-gx-modal", "n_clicks"), 
    Input("close-gx-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gx-modal", "close-gx-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("gy-modal-body", "children"), 
    Output("gy-modal", "is_open"),
    Output("gy_graph", "children", allow_duplicate=True), 
    State("gy_graph", "children"), 
    State("gy-modal-body", "children"), 
    State("gy-modal", "is_open"),
    Input("open-gy-modal", "n_clicks"), 
    Input("close-gy-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gy-modal", "close-gy-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("gz-modal-body", "children"), 
    Output("gz-modal", "is_open"),
    Output("gz_graph", "children", allow_duplicate=True), 
    State("gz_graph", "children"), 
    State("gz-modal-body", "children"), 
    State("gz-modal", "is_open"),
    Input("open-gz-modal", "n_clicks"), 
    Input("close-gz-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gz-modal", "close-gz-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("ax-modal-body", "children"), 
    Output("ax-modal", "is_open"),
    Output("ax_graph", "children", allow_duplicate=True), 
    State("ax_graph", "children"), 
    State("ax-modal-body", "children"), 
    State("ax-modal", "is_open"),
    Input("open-ax-modal", "n_clicks"), 
    Input("close-ax-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-ax-modal", "close-ax-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("ay-modal-body", "children"), 
    Output("ay-modal", "is_open"),
    Output("ay_graph", "children", allow_duplicate=True), 
    State("ay_graph", "children"), 
    State("ay-modal-body", "children"), 
    State("ay-modal", "is_open"),
    Input("open-ay-modal", "n_clicks"), 
    Input("close-ay-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-ay-modal", "close-ay-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("az-modal-body", "children"), 
    Output("az-modal", "is_open"),
    Output("az_graph", "children", allow_duplicate=True), 
    State("az_graph", "children"), 
    State("az-modal-body", "children"), 
    State("az-modal", "is_open"),
    Input("open-az-modal", "n_clicks"), 
    Input("close-az-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-az-modal", "close-az-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("pIb-modal-body", "children"), 
    Output("pIb-modal", "is_open"),
    Output("pIb_graph", "children", allow_duplicate=True), 
    State("pIb_graph", "children"), 
    State("pIb-modal-body", "children"), 
    State("pIb-modal", "is_open"),
    Input("open-pIb-modal", "n_clicks"), 
    Input("close-pIb-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-pIb-modal", "close-pIb-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("hIb-modal-body", "children"), 
    Output("hIb-modal", "is_open"),
    Output("hIb_graph", "children", allow_duplicate=True), 
    State("hIb_graph", "children"), 
    State("hIb-modal-body", "children"), 
    State("hIb-modal", "is_open"),
    Input("open-hIb-modal", "n_clicks"), 
    Input("close-hIb-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-hIb-modal", "close-hIb-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("v2b-modal-body", "children"), 
    Output("v2b-modal", "is_open"),
    Output("v2b_graph", "children", allow_duplicate=True), 
    State("v2b_graph", "children"), 
    State("v2b-modal-body", "children"), 
    State("v2b-modal", "is_open"),
    Input("open-v2b-modal", "n_clicks"), 
    Input("close-v2b-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-v2b-modal", "close-v2b-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("vFb-modal-body", "children"), 
    Output("vFb-modal", "is_open"),
    Output("vFb_graph", "children", allow_duplicate=True), 
    State("vFb_graph", "children"), 
    State("vFb-modal-body", "children"), 
    State("vFb-modal", "is_open"),
    Input("open-vFb-modal", "n_clicks"), 
    Input("close-vFb-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-vFb-modal", "close-vFb-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("cFb-modal-body", "children"), 
    Output("cFb-modal", "is_open"),
    Output("cFb_graph", "children", allow_duplicate=True), 
    State("cFb_graph", "children"), 
    State("cFb-modal-body", "children"), 
    State("cFb-modal", "is_open"),
    Input("open-cFb-modal", "n_clicks"), 
    Input("close-cFb-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-cFb-modal", "close-cFb-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("c2b-modal-body", "children"), 
    Output("c2b-modal", "is_open"),
    Output("c2b_graph", "children", allow_duplicate=True), 
    State("c2b_graph", "children"), 
    State("c2b-modal-body", "children"), 
    State("c2b-modal", "is_open"),
    Input("open-c2b-modal", "n_clicks"), 
    Input("close-c2b-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-c2b-modal", "close-c2b-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("tIb-modal-body", "children"), 
    Output("tIb-modal", "is_open"),
    Output("tIb_graph", "children", allow_duplicate=True), 
    State("tIb_graph", "children"), 
    State("tIb-modal-body", "children"), 
    State("tIb-modal", "is_open"),
    Input("open-tIb-modal", "n_clicks"), 
    Input("close-tIb-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-tIb-modal", "close-tIb-modal", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("sumspec-card1-modalbody-id", "children"), 
    Output("sumspec-card1-modal-id", "is_open"),
    Output("sumspec1", "children", allow_duplicate=True), 
    State("sumspec1", "children"), 
    State("sumspec-card1-modalbody-id", "children"), 
    State("sumspec-card1-modal-id", "is_open"),
    Input("sumspec-card1-expand-button-id", "n_clicks"), 
    Input("sumspec-card1-close-button-id", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "sumspec-card1-expand-button-id", "sumspec-card1-close-button-id", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("sumspec-card2-modalbody-id", "children"), 
    Output("sumspec-card2-modal-id", "is_open"),
    Output("sumspec2", "children", allow_duplicate=True), 
    State("sumspec2", "children"), 
    State("sumspec-card2-modalbody-id", "children"), 
    State("sumspec-card2-modal-id", "is_open"),
    Input("sumspec-card2-expand-button-id", "n_clicks"), 
    Input("sumspec-card2-close-button-id", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "sumspec-card2-expand-button-id", "sumspec-card2-close-button-id", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("sumspec-card3-modalbody-id", "children"), 
    Output("sumspec-card3-modal-id", "is_open"),
    Output("sumspec3", "children", allow_duplicate=True), 
    State("sumspec3", "children"), 
    State("sumspec-card3-modalbody-id", "children"), 
    State("sumspec-card3-modal-id", "is_open"),
    Input("sumspec-card3-expand-button-id", "n_clicks"), 
    Input("sumspec-card3-close-button-id", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "sumspec-card3-expand-button-id", "sumspec-card3-close-button-id", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("open-waveform-modal-body", "children"), 
    Output("open-waveform-modal", "is_open"),
    Output("waveformgraph", "children", allow_duplicate=True), 
    State("waveformgraph", "children"), 
    State("open-waveform-modal-body", "children"), 
    State("open-waveform-modal", "is_open"),
    Input("open-waveform-button", "n_clicks"), 
    Input("close-waveform-button", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-waveform-button", "close-waveform-button", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("open-spec-modal-body", "children"), 
    Output("open-spec-modal", "is_open"),
    Output("spectrogramgraph", "children", allow_duplicate=True), 
    State("spectrogramgraph", "children"), 
    State("open-spec-modal-body", "children"), 
    State("open-spec-modal", "is_open"),
    Input("open-spec-button", "n_clicks"), 
    Input("close-spec-button", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-spec-button", "close-spec-button", modal_open, 
                  modal_graph, page_graph)

@app.callback(
    Output("open-psd-modal-body", "children"), 
    Output("open-psd-modal", "is_open"),
    Output("psdgraph", "children", allow_duplicate=True), 
    State("psdgraph", "children"), 
    State("open-psd-modal-body", "children"), 
    State("open-psd-modal", "is_open"),
    Input("open-psd-button", "n_clicks"), 
    Input("close-psd-button", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-psd-button", "close-psd-button", modal_open, 
                  modal_graph, page_graph)
        
@app.callback(
    Output("gps-east-modal-body", "children"), 
    Output("gps-east-modal", "is_open"),
    Output("gps_east_graph", "children", allow_duplicate=True), 
    State("gps_east_graph", "children"), 
    State("gps-east-modal-body", "children"), 
    State("gps-east-modal", "is_open"),
    Input("open-gps-east-modal", "n_clicks"), 
    Input("close-gps-east-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gps-east-modal", "close-gps-east-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gps-north-modal-body", "children"), 
    Output("gps-north-modal", "is_open"),
    Output("gps_north_graph", "children", allow_duplicate=True), 
    State("gps_north_graph", "children"), 
    State("gps-north-modal-body", "children"), 
    State("gps-north-modal", "is_open"),
    Input("open-gps-north-modal", "n_clicks"), 
    Input("close-gps-north-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gps-north-modal", "close-gps-north-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gps-up-modal-body", "children"), 
    Output("gps-up-modal", "is_open"),
    Output("gps_up_graph", "children", allow_duplicate=True), 
    State("gps_up_graph", "children"), 
    State("gps-up-modal-body", "children"), 
    State("gps-up-modal", "is_open"),
    Input("open-gps-up-modal", "n_clicks"), 
    Input("close-gps-up-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gps-up-modal", "close-gps-up-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("weather-temp-modal-body", "children"), 
    Output("weather-temp-modal", "is_open"),
    Output("weather_temp_graph", "children", allow_duplicate=True), 
    State("weather_temp_graph", "children"), 
    State("weather-temp-modal-body", "children"), 
    State("weather-temp-modal", "is_open"),
    Input("open-weather-temp-modal", "n_clicks"), 
    Input("close-weather-temp-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-weather-temp-modal", "close-weather-temp-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("weather-press-modal-body", "children"), 
    Output("weather-press-modal", "is_open"),
    Output("weather_pressure_graph", "children", allow_duplicate=True), 
    State("weather_pressure_graph", "children"), 
    State("weather-press-modal-body", "children"), 
    State("weather-press-modal", "is_open"),
    Input("open-weather-press-modal", "n_clicks"), 
    Input("close-weather-press-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-weather-press-modal", "close-weather-press-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("weather-hum-modal-body", "children"), 
    Output("weather-hum-modal", "is_open"),
    Output("weather_humidity_graph", "children", allow_duplicate=True), 
    State("weather_humidity_graph", "children"), 
    State("weather-hum-modal-body", "children"), 
    State("weather-hum-modal", "is_open"),
    Input("open-weather-hum-modal", "n_clicks"), 
    Input("close-weather-hum-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-weather-hum-modal", "close-weather-hum-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gpsvis-ani-modal-body", "children"), 
    Output("gpsvis-ani-modal", "is_open"),
    Output("gps_animation_div", "children", allow_duplicate=True), 
    State("gps_animation_div", "children"), 
    State("gpsvis-ani-modal-body", "children"), 
    State("gpsvis-ani-modal", "is_open"),
    Input("open-gpsvis-ani-modal", "n_clicks"), 
    Input("close-gpsvis-ani-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gpsvis-ani-modal", "close-gpsvis-ani-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gpsvis-ani2-modal-body", "children"), 
    Output("gpsvis-ani2-modal", "is_open"),
    Output("gps_animation2", "children", allow_duplicate=True), 
    State("gps_animation2", "children"), 
    State("gpsvis-ani2-modal-body", "children"), 
    State("gpsvis-ani2-modal", "is_open"),
    Input("open-gpsvis-ani2-modal", "n_clicks"), 
    Input("close-gpsvis-ani2-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gpsvis-ani2-modal", "close-gpsvis-ani2-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gpsvis-base-modal-body", "children"), 
    Output("gpsvis-base-modal", "is_open"),
    Output("baseline_length", "children", allow_duplicate=True), 
    State("baseline_length", "children"), 
    State("gpsvis-base-modal-body", "children"), 
    State("gpsvis-base-modal", "is_open"),
    Input("open-gpsvis-base-modal", "n_clicks"), 
    Input("close-gpsvis-base-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gpsvis-base-modal", "close-gpsvis-base-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gpsvis-orient-modal-body", "children"), 
    Output("gpsvis-orient-modal", "is_open"),
    Output("baseline_orient", "children", allow_duplicate=True), 
    State("baseline_orient", "children"), 
    State("gpsvis-orient-modal-body", "children"), 
    State("gpsvis-orient-modal", "is_open"),
    Input("open-gpsvis-orient-modal", "n_clicks"), 
    Input("close-gpsvis-orient-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gpsvis-orient-modal", "close-gpsvis-orient-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gpsvis-lengthres-modal-body", "children"), 
    Output("gpsvis-lengthres-modal", "is_open"),
    Output("baseline_length_resid", "children", allow_duplicate=True), 
    State("baseline_length_resid", "children"), 
    State("gpsvis-lengthres-modal-body", "children"), 
    State("gpsvis-lengthres-modal", "is_open"),
    Input("open-gpsvis-lengthres-modal", "n_clicks"), 
    Input("close-gpsvis-lengthres-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gpsvis-lengthres-modal", "close-gpsvis-lengthres-modal", modal_open,
                         modal_graph, page_graph)

@app.callback(
    Output("gpsvis-orientres-modal-body", "children"), 
    Output("gpsvis-orientres-modal", "is_open"),
    Output("baseline_orient_resid", "children", allow_duplicate=True), 
    State("baseline_orient_resid", "children"), 
    State("gpsvis-orientres-modal-body", "children"), 
    State("gpsvis-orientres-modal", "is_open"),
    Input("open-gpsvis-orientres-modal", "n_clicks"), 
    Input("close-gpsvis-orientres-modal", "n_clicks"),
    prevent_initial_call=True,
)
def handle_open_close(page_graph, modal_graph, modal_open, open_button_click, close_button_click):
    return update_expand(ctx, "open-gpsvis-orientres-modal", "close-gpsvis-orientres-modal", modal_open,
                         modal_graph, page_graph)

## Main website callback to update page content based on navbar selection 
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        all_home_elements = get_all_home_elements()
        return dbc.Container(all_home_elements, fluid=True)
    elif pathname == "/seismic":
        return dbc.Container(seismic.get_all_seismic_elements(), fluid=True)
    elif pathname == "/weather":
        return dbc.Container(weather.get_all_weather_elements(), fluid=True)
    elif pathname == "/gps":
        return dbc.Container(gps.get_all_gps_elements(), fluid=True)
    elif pathname =="/gpsdeform":
        return dbc.Container(gpsvis.get_all_gpsvis_elements(), fluid=True)
    elif pathname == "/monvct":
        return dbc.Container(monvct.get_all_monvct_elements(), fluid=True)
    elif pathname == "/monph":
        return dbc.Container(monph.get_all_monph_elements(), fluid=True)
    elif pathname == "/monga":
        return dbc.Container(monga.get_all_monga_elements(), fluid=True)
    elif pathname == "/monu":
        return dbc.Container(monu.get_all_monu_elements(), fluid=True)
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
    app.run_server(host="0.0.0.0", port="8080", debug=True)