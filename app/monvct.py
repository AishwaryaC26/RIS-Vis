import dash_bootstrap_components as dbc
import elementstyling, componentbuilder
import componentbuilder

form_desc = "Use this form to visualize voltage, current, and temperature data of the SGIP."

v2b_desc = "This graph displays voltage to the battery over time."

vFb_desc = "This graph displays voltage from the battery over time."

c2b_desc = "This graph displays current to the battery over time."

cFb_desc = "This graph displays current from the battery over time."

tIb_desc = "This graph displays temperature inside the battery over time."

# method to get all voltage, current, & temperature page components
def get_all_monvct_elements():
    monvct_form = componentbuilder.build_form_component("Voltage, Current, & Temperature Data Visualization Form", [], 
                                                     [("Select date range:", "monvct_datepicker")], "monvct_formsubmitbut", "open-monvctq-button", "monvctq-modal", form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    v2b_graph = componentbuilder.build_graph_component("Voltage (V) to Battery", "open-v2b-modal", 
                                                            "close-v2b-modal", "open-v2b-q-button", "v2b-modal-body", "v2b-modal", "v2b_graph", "v2b-q-modal", v2b_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monvct_rowone = dbc.Row([dbc.Col([monvct_form], width = 4), dbc.Col([v2b_graph], width = 8)])
    vFb_graph = componentbuilder.build_graph_component("Voltage (V) from Battery", "open-vFb-modal", 
                                                             "close-vFb-modal", "open-vFb-q-button", "vFb-modal-body", "vFb-modal", 
                                                             "vFb_graph",  "vFb-q-modal", vFb_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    c2b_graph = componentbuilder.build_graph_component("Current (A) to Battery", "open-c2b-modal", 
                                                            "close-c2b-modal", "open-c2b-q-button", "c2b-modal-body", "c2b-modal", "c2b_graph", "c2b-q-modal", c2b_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monvct_rowtwo = dbc.Row([dbc.Col([vFb_graph], width = 6), dbc.Col([c2b_graph], width = 6)])
    cFb_graph = componentbuilder.build_graph_component("Current (A) from Battery", "open-cFb-modal", 
                                                             "close-cFb-modal", "open-cFb-q-button", "cFb-modal-body", "cFb-modal", 
                                                             "cFb_graph",  "cFb-q-modal", cFb_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    tIb_graph = componentbuilder.build_graph_component("Temperature (C) inside the Box", "open-tIb-modal", 
                                                            "close-tIb-modal", "open-tIb-q-button", "tIb-modal-body", "tIb-modal", "tIb_graph", "tIb-q-modal", tIb_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    monvct_rowthree = dbc.Row([dbc.Col([cFb_graph], width = 6), dbc.Col([tIb_graph], width = 6)])

    return [monvct_rowone, monvct_rowtwo, monvct_rowthree]