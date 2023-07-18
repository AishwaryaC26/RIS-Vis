import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta 
import ast, os
from dotenv import load_dotenv

# GPS Visualization Page Elements
load_dotenv()

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
    gps_form = get_date_picker()
    gps_animation = dbc.Card(dbc.Spinner([html.Div(id="gps_animation")], color="primary"),  body=True, style=elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    gps_row_one = dbc.Row([dbc.Col([gps_form], width = 3), dbc.Col([gps_animation], width = 9)])
    
    gps_form2 = get_date_picker2()
    gps_animation2 = dbc.Card(dbc.Spinner([html.Div(id="gps_animation2")], color="primary"),  body=True, style=elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    gps_row_two = dbc.Row([dbc.Col(gps_form2, width = 4), dbc.Col([gps_animation2], width = 8)])

    baseline_length = dbc.Card(["Baseline Length Graph", html.Br(), html.Br(), dbc.Spinner(html.Div(id = "baseline_length"), color = "primary")],  body=True, style = elementstyling.CARD_HALF_WIDTH_LEFT)

    baseline_orientation = dbc.Card(["Baseline Orientation Graph", html.Br(), html.Br(), dbc.Spinner(html.Div(id = "baseline_orient"), color="primary")],  body=True, style = elementstyling.CARD_HALF_WIDTH_RIGHT)

    baseline_first_row = dbc.Row([dbc.Col(baseline_length, width = 6), dbc.Col(baseline_orientation, width = 6)])

    baseline_length_residual = dbc.Card(["Baseline Length Residual Graph", html.Br(), html.Br(), dbc.Spinner(html.Div(id = "baseline_length_resid"), color = "primary")],  body=True, style = elementstyling.CARD_HALF_WIDTH_LEFT)

    baseline_orientation_residual = dbc.Card(["Baseline Length Residual Orientation Graph", html.Br(), html.Br(), dbc.Spinner(html.Div(id = "baseline_orient_resid"), color="primary")],  body=True, style = elementstyling.CARD_HALF_WIDTH_RIGHT)
    
    baseline_second_row = dbc.Row([dbc.Col(baseline_length_residual, width = 6), dbc.Col(baseline_orientation_residual, width = 6)])

    return [gps_row_one, gps_row_two, baseline_first_row, html.Br(), baseline_second_row]