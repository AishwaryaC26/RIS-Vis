import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling, componentbuilder
from datetime import date, timedelta 
import componentbuilder


form_desc = "Use this form to visualize CPU Usage, Memory Usage, and Free Disk Space of the SGIP over time."

cu_desc = "This graph displays SGIP CPU Usage over time."

mu_desc = "This graph displays SGIP Memory Usage over time."

fu_desc = "This graph displays SGIP Free Disk Space over time."

# method to get all utility page components
def get_all_monu_elements():
    monu_form = componentbuilder.build_form_component("Utility Data Visualization Form", [], 
                                                     [("Select date range:", "u_datepicker")], "monu_formsubmitbut", "open-monuq-button", "monuq-modal", form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    cu_graph = componentbuilder.build_graph_component("CPU Usage (%)", "open-cu-modal", 
                                                            "close-cu-modal", "open-cu-q-button", "cu-modal-body", "cu-modal", "cu_graph", "cu-q-modal", cu_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monu_rowone = dbc.Row([dbc.Col([monu_form], width = 4), dbc.Col([cu_graph], width = 8)])
    mu_graph = componentbuilder.build_graph_component("Memory Usage (%)", "open-mu-modal", 
                                                             "close-mu-modal", "open-mu-q-button", "mu-modal-body", "mu-modal", 
                                                             "mu_graph",  "mu-q-modal", mu_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    fu_graph = componentbuilder.build_graph_component("Free Disk Space (GB)", "open-fu-modal", 
                                                             "close-fu-modal", "open-fu-q-button", "fu-modal-body", "fu-modal", 
                                                             "fu_graph",  "fu-q-modal", fu_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    
    monu_rowtwo = dbc.Row([dbc.Col([mu_graph], width = 6), dbc.Col([fu_graph], width = 6)])
    return [monu_rowone, monu_rowtwo]