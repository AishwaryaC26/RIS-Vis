import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta 
import ast, os

def get_date_picker():
    #Time frame picker
    gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])
    #Dropdown to choose gps station
    if gps_stations:
        dropdown_gps_station = html.Div(
            [
                dbc.Label("Select GPS station:"),
                dcc.Dropdown(
                    gps_stations,
                    gps_stations[0],
                    id="gps_dropdown",
                    clearable=False,
                ),
            ],
        )
    else:
        dropdown_gps_station = html.Div()

    datePicker = html.Div(
        [   dbc.Row([dbc.Label("Select date range:")]),    
            dcc.DatePickerRange(
            id='gps_datepicker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date(2022, 12, 1),
            start_date=date.today() - timedelta(10),
            end_date=date.today()
        )
        ],
    )
    gps_date_pick = dbc.Form([dropdown_gps_station, html.Br(), datePicker, html.Br(), dbc.Button("Submit", color="primary",
                                            className="mb-3", id = "gps_formsubmitbut")])
    
    return dbc.Card([gps_date_pick],  body=True, style=elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

def get_all_gps_elements():
    gps_form = get_date_picker()
    gps_east_graph = dbc.Card(dbc.Spinner([html.Div(id="gps_east_graph")], color="primary"),  body=True, style=elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    gps_row_one = dbc.Row([dbc.Col([gps_form], width = 3), dbc.Col([gps_east_graph])])
    gps_north_graph = dbc.Card(dbc.Spinner([html.Div(id="gps_north_graph")], color="primary"),  body=True, style=elementstyling.MARGIN_STYLE)
    gps_up_graph = dbc.Card(dbc.Spinner([html.Div(id="gps_up_graph")], color="primary"),  body=True, style=elementstyling.MARGIN_STYLE)
    return [gps_row_one, gps_north_graph, gps_up_graph]