import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta


def get_date_picker():
    #Time frame picker
    datePicker = html.Div(
        [   dbc.Row([dbc.Label("Select date range:")]),    
            dcc.DatePickerRange(
            id='weather_datepicker',
            min_date_allowed=date(1900, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date(2022, 12, 1),
            start_date=date.today() - timedelta(10),
            end_date=date.today()
        )
        ],

    )
    weather_date_pick = dbc.Form([datePicker, html.Br(), dbc.Button("Submit", color="primary",
                                        className="mb-3", id = "weather_formsubmitbut")])
    weather_form =  dbc.Card([weather_date_pick],  body=True, style=elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    return weather_form


def get_all_weather_elements():
    weather_form = get_date_picker()
    weather_temp_graph = dbc.Card(dbc.Spinner([html.Div(id="weather_temp_graph")], color="primary"),  body=True, style=elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    weather_row_one = dbc.Row([dbc.Col([weather_form], width = 4), dbc.Col([weather_temp_graph], width = 8)])
    weather_pressure = dbc.Card(dbc.Spinner([html.Div(id="weather_pressure_graph")], color="primary"),  body=True, style=elementstyling.MARGIN_STYLE)
    weather_humidity = dbc.Card(dbc.Spinner([html.Div(id="weather_humidity_graph")], color="primary"),  body=True, style=elementstyling.MARGIN_STYLE)
    return [weather_row_one, weather_pressure, weather_humidity]
