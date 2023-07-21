import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta 
import ast, os
from dotenv import load_dotenv
import componentbuilder

# GPS Visualization Page Elements
load_dotenv()

gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])

def get_date_picker(): ## Date picker for animation section
    #Time frame picker
    gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])
    #Dropdown to choose gps station
    if gps_stations:
        dropdown_gpsvis_station = html.Div(
            [
                dbc.Label("Select GPS station:"),
                dcc.Dropdown(
                    gps_stations,
                    gps_stations[0],
                    id="gps_vis_dropdown",
                    clearable=False,
                ),
            ],
        )
    else:
        dropdown_gpsvis_station = html.Div()

    datePicker = html.Div(
        [   dbc.Row([dbc.Label("Select date range:")]),    
            dcc.DatePickerRange(
            id='gps_vis_datepicker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date(2022, 12, 1),
            start_date=date.today() - timedelta(10),
            end_date=date.today()
        )
        ],
    )
    gps_date_pick = dbc.Form([dropdown_gpsvis_station, html.Br(), datePicker, html.Br(), dbc.Button("Submit", color="primary",
                                            className="mb-3", id = "gpsvis_formsubmitbut")])
    
    return dbc.Card([gps_date_pick],  body=True, style=elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

def get_date_picker2(): ## Datepicker for relative movement section
    #Time frame picker
    gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])
    #Dropdown to choose gps station
    if gps_stations:
        dropdown_gpsvis_station = html.Div(
            [
                dbc.Label("Select Reference GPS station:"),
                dcc.Dropdown(
                    gps_stations,
                    gps_stations[0],
                    id="gps_vis_dropdown2",
                    clearable=False,
                ),
            ],
        )
    else:
        dropdown_gpsvis_station = html.Div()

    datePicker = html.Div(
        [   dbc.Row([dbc.Label("Select date range:")]),    
            dcc.DatePickerRange(
            id='gps_vis_datepicker2',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date(2022, 12, 1),
            start_date=date.today() - timedelta(10),
            end_date=date.today()
        )
        ],
    )
    gps_date_pick = dbc.Form([dropdown_gpsvis_station, html.Br(), datePicker, html.Br(), dbc.Button("Submit", color="primary",
                                            className="mb-3", id = "gpsvis_formsubmitbut2")])
    
    return dbc.Card([gps_date_pick],  body=True, style=elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

def get_all_gpsvis_elements():
    gps_form = componentbuilder.build_form_component("GPS Tracks Form", [], [("Select date range:", 'gps_vis_datepicker'),], "gpsvis_formsubmitbut", "open-gpsvis1q-button", "gpsvis1-q-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

    gps_animation = componentbuilder.build_graph_component("Tracks of GPS Stations", "open-gpsvis-ani-modal", 
                                                            "close-gpsvis-ani-modal", "open-gpsvis-ani-q-button", "gpsvis-ani-modal-body", "gpsvis-ani-modal", "gps_animation", "gpsvis-ani-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP, True)
    
    gps_row_one = dbc.Row([dbc.Col([gps_form], width = 4), dbc.Col([gps_animation], width = 8)])
    
    gps_form2 = componentbuilder.build_form_component("Deformation Visualization Form", [("Select Reference GPS station:", gps_stations, "gps_vis_dropdown2")], [("Select date range:", "gps_vis_datepicker2")], "gpsvis_formsubmitbut2", "open-gpsvis2q-button", "gpsvis2-q-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

    gps_animation2 = componentbuilder.build_graph_component("Relative Movement over Time", "open-gpsvis-ani2-modal", 
                                                            "close-gpsvis-ani2-modal", "open-gpsvis-ani2-q-button", "gpsvis-ani2-modal-body", "gpsvis-ani2-modal", "gps_animation2", "gpsvis-ani2-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP,)

    gps_row_two = dbc.Row([dbc.Col(gps_form2, width = 4), dbc.Col([gps_animation2,], width = 8)])

    baseline_length = componentbuilder.build_graph_component("Baseline Length Graph", "open-gpsvis-base-modal", 
                                                            "close-gpsvis-base-modal", "open-gpsvis-base-q-button", "gpsvis-base-modal-body", "gpsvis-base-modal", "baseline_length", "gpsvis-base-q-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT)

    baseline_orientation = componentbuilder.build_graph_component("Baseline Orientation Graph", "open-gpsvis-orient-modal", 
                                                            "close-gpsvis-orient-modal", "open-gpsvis-orient-q-button", "gpsvis-orient-modal-body", "gpsvis-orient-modal", "baseline_orient", "gpsvis-orient-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT)

    baseline_first_row = dbc.Row([dbc.Col(baseline_length, width = 6), dbc.Col(baseline_orientation, width = 6)])

    baseline_length_residual = componentbuilder.build_graph_component("Baseline Length Residual Graph", "open-gpsvis-lengthres-modal", 
                                                            "close-gpsvis-lengthres-modal", "open-gpsvis-lengthres-q-button", "gpsvis-lengthres-modal-body", "gpsvis-lengthres-modal", "baseline_length_resid", "gpsvis-lengthres-q-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWN)

    baseline_orientation_residual = componentbuilder.build_graph_component("Baseline Orientation Residual Graph", "open-gpsvis-orientres-modal",  
                                                            "close-gpsvis-orientres-modal", "open-gpsvis-orientres-q-button", "gpsvis-orientres-modal-body", "gpsvis-orientres-modal", "baseline_orient_resid", "gpsvis-orientres-q-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWN)
    
    baseline_second_row = dbc.Row([dbc.Col(baseline_length_residual, width = 6), dbc.Col(baseline_orientation_residual, width = 6), html.Br(), html.Br()])

    return [gps_row_one, gps_row_two, baseline_first_row, html.Br(), baseline_second_row]