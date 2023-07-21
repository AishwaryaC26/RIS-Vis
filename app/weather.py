import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta
import componentbuilder


def get_all_weather_elements():
    weather_form = componentbuilder.build_form_component("Weather Data Visualization Form", [], [("Select date range:", "weather_datepicker",)], "weather_formsubmitbut", "open-weatherq-button", "weather-q-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    weather_temp_graph = componentbuilder.build_graph_component("Temperature", "open-weather-temp-modal", 
                                                            "close-weather-temp-modal", "open-weather-tempq-button", "weather-temp-modal-body", "weather-temp-modal", "weather_temp_graph", "weather-temp-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    weather_row_one = dbc.Row([dbc.Col([weather_form], width = 4), dbc.Col([weather_temp_graph], width = 8)])
    weather_pressure_graph = componentbuilder.build_graph_component("Pressure", "open-weather-press-modal", 
                                                            "close-weather-press-modal", "open-weather-pressq-button", "weather-press-modal-body", "weather-press-modal", "weather_pressure_graph", "weather-press-q-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    weather_humidity_graph = componentbuilder.build_graph_component("Relative Humidity", "open-weather-hum-modal", 
                                                            "close-weather-hum-modal", "open-weather-humq-button", "weather-hum-modal-body", "weather-hum-modal", "weather_humidity_graph", "weather-hum-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    weather_row_two = dbc.Row([dbc.Col([weather_pressure_graph], width = 6), dbc.Col([weather_humidity_graph], width = 6)])
    return [weather_row_one, weather_row_two]
