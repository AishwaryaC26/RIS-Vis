import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling, componentbuilder
from datetime import date, timedelta 
import componentbuilder

form_desc = "Use the form to visualize pressure and humidity data of the SGIP."

pib_desc = "This graph displays pressure inside the SGIP over time."

hib_desc = "This graph displays humidity inside the SGIP over time."

def get_all_monph_elements():
    monph_form = componentbuilder.build_form_component("Pressure & Humidity Data Visualization Form", [], 
                                                     [("Select date range:", "ph_datepicker")], "monph_formsubmitbut", "open-monphq-button", "monphq-modal", form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    pIb_graph = componentbuilder.build_graph_component("Pressure Inside the Box (mb)", "open-pIb-modal", 
                                                            "close-pIb-modal", "open-pIb-q-button", "pIb-modal-body", "pIb-modal", "pIb_graph", "pIb-q-modal", pib_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monph_rowone = dbc.Row([dbc.Col([monph_form], width = 4), dbc.Col([pIb_graph], width = 8)])
    hIb_graph = componentbuilder.build_graph_component("Humidity Inside the Box (%)", "open-hIb-modal", 
                                                             "close-hIb-modal", "open-hIb-q-button", "hIb-modal-body", "hIb-modal", 
                                                             "hIb_graph",  "hIb-q-modal", hib_desc, elementstyling.MARGIN_STYLE)
    monph_rowtwo = dbc.Row([dbc.Col([hIb_graph], width = 12)])
    

    return [monph_rowone, monph_rowtwo]