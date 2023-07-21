import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling, componentbuilder
from datetime import date, timedelta 
import ast, os
import componentbuilder
from dotenv import load_dotenv


load_dotenv()
gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])

def get_all_gps_elements():
    gps_form = componentbuilder.build_form_component("GPS Data Visualization Form", [("Select GPS station:", gps_stations, "gps_dropdown"),], 
                                                     [("Select date range:", "gps_datepicker")], "gps_formsubmitbut", "open-gpsq-button", "gpsq-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    gps_east_graph = componentbuilder.build_graph_component("East Movement", "open-gps-east-modal", 
                                                            "close-gps-east-modal", "open-gps-east-q-button", "gps-east-modal-body", "gps-east-modal", "gps_east_graph", "gps-east-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    gps_row_one = dbc.Row([dbc.Col([gps_form], width = 4), dbc.Col([gps_east_graph], width = 8)])
    gps_north_graph = componentbuilder.build_graph_component("North Movement", "open-gps-north-modal", 
                                                             "close-gps-north-modal", "open-gps-north-q-button", "gps-north-modal-body", "gps-north-modal", 
                                                             "gps_north_graph",  "gps-north-q-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    gps_up_graph = componentbuilder.build_graph_component("Up Movement", "open-gps-up-modal", 
                                                             "close-gps-up-modal", "open-gps-up-q-button", "gps-up-modal-body", "gps-up-modal", 
                                                             "gps_up_graph", "gps-up-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    gps_row_two = dbc.Row([dbc.Col([gps_north_graph], width = 6), dbc.Col([gps_up_graph], width = 6)])
    return [gps_row_one, gps_row_two]