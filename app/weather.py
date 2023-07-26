import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta
import componentbuilder
import os, ast
from dotenv import load_dotenv

load_dotenv()
coords = ast.literal_eval(os.environ["WEATHER_STATION_COORDS"])

form_desc = "Weather data is collected from the AWS (Automatic Weather Station) weather database organized by the University of Wisconsin. \
    The particular station being used is the Marilyn Station in Ross Ice Shelf. Use the Weather Data Visualization Form to visualize \
        temperature, humidity, and pressure measurements over time."

temp_desc = "This graph displays change in temperature over time."

pressure_desc = "This graph displays change in pressure over time."

humid_desc = "This graph displays change in relative humidity over time."

def get_all_weather_elements():
    weather_form = componentbuilder.build_form_component("Weather Data Visualization Form", [], [("Select date range:", "weather_datepicker",)], "weather_formsubmitbut", "open-weatherq-button", "weather-q-modal", form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP, coords)
    weather_temp_graph = componentbuilder.build_graph_component("Temperature", "open-weather-temp-modal", 
                                                            "close-weather-temp-modal", "open-weather-tempq-button", "weather-temp-modal-body", "weather-temp-modal", "weather_temp_graph", "weather-temp-q-modal", temp_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    weather_row_one = dbc.Row([dbc.Col([weather_form], width = 4), dbc.Col([weather_temp_graph], width = 8)])
    weather_pressure_graph = componentbuilder.build_graph_component("Pressure", "open-weather-press-modal", 
                                                            "close-weather-press-modal", "open-weather-pressq-button", "weather-press-modal-body", "weather-press-modal", "weather_pressure_graph", "weather-press-q-modal", pressure_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    weather_humidity_graph = componentbuilder.build_graph_component("Relative Humidity", "open-weather-hum-modal", 
                                                            "close-weather-hum-modal", "open-weather-humq-button", "weather-hum-modal-body", "weather-hum-modal", "weather_humidity_graph", "weather-hum-q-modal", humid_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    weather_row_two = dbc.Row([dbc.Col([weather_pressure_graph], width = 6), dbc.Col([weather_humidity_graph], width = 6)])
    return [weather_row_one, weather_row_two]
