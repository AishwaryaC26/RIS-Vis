import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling, componentbuilder
from datetime import date, timedelta 
import componentbuilder

form_desc = "Use the form to track gyroscope and acceleration data of the SGIP."

gx_desc = "This graph displays gyroscope movements in the X direction."

gy_desc = "This graph displays gyroscope movements in the Y direction."

gz_desc = "This graph displays gyroscope movements in the Z direction."

ax_desc = "This graph displays acceleration in the X direction."

ay_desc = "This graph displays acceleration in the X direction."

az_desc = "This graph displays acceleration in the X direction."


def get_all_monga_elements():
    monga_form = componentbuilder.build_form_component("Gyroscope & Acceleration Data Visualization Form", [], 
                                                     [("Select date range:", "monga_datepicker")], "monga_formsubmitbut", "open-mongaq-button", "mongaq-modal", form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    gx_graph = componentbuilder.build_graph_component("Gyroscope X (deg/s)", "open-gx-modal", 
                                                            "close-gx-modal", "open-gx-q-button", "gx-modal-body", "gx-modal", "gx_graph", "gx-q-modal", gx_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monga_rowone = dbc.Row([dbc.Col([monga_form], width = 4), dbc.Col([gx_graph], width = 8)])
    gy_graph = componentbuilder.build_graph_component("Gyroscope Y (deg/s)", "open-gy-modal", 
                                                             "close-gy-modal", "open-gy-q-button", "gy-modal-body", "gy-modal", 
                                                             "gy_graph",  "gy-q-modal", gy_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    gz_graph = componentbuilder.build_graph_component("Gyroscope Z (deg/s)", "open-gz-modal", 
                                                            "close-gz-modal", "open-gz-q-button", "gz-modal-body", "gz-modal", "gz_graph", "gz-q-modal", gz_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monga_rowtwo = dbc.Row([dbc.Col([gy_graph], width = 6), dbc.Col([gz_graph], width = 6)])
    ax_graph = componentbuilder.build_graph_component("Accelerometer X (m/s^2)", "open-ax-modal", 
                                                             "close-ax-modal", "open-ax-q-button", "ax-modal-body", "ax-modal", 
                                                             "ax_graph",  "ax-q-modal", ax_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    ay_graph = componentbuilder.build_graph_component("Accelerometer Y (m/s^2)", "open-ay-modal", 
                                                            "close-ay-modal", "open-ay-q-button", "ay-modal-body", "ay-modal", "ay_graph", "ay-q-modal", ay_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monga_rowthree = dbc.Row([dbc.Col([ax_graph], width = 6), dbc.Col([ay_graph], width = 6)])
    az_graph = componentbuilder.build_graph_component("Accelerometer Z (m/s^2)", "open-az-modal", 
                                                            "close-az-modal", "open-az-q-button", "az-modal-body", "az-modal", "az_graph", "az-q-modal", az_desc, elementstyling.MARGIN_STYLE)
    monga_rowfour = dbc.Row([dbc.Col([az_graph], width = 12)])
    return [monga_rowone, monga_rowtwo, monga_rowthree, monga_rowfour]