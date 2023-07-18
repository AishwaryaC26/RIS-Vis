import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date
import os, ast
from dotenv import load_dotenv

load_dotenv()
stations = ast.literal_eval(os.environ["SEISMIC_STATIONS"])

#create list of stations from "stations" dict
stationsoptions = list(stations.keys())

#Dropdown to choose seismic station
dropdown_seismic_station = html.Div(
    [
        dbc.Label("Select seismic station:"),
        dcc.Dropdown(
            stationsoptions,
            stationsoptions[0],
            id="dropdownseismic",
            clearable=False,
        ),
    ],

)

#Time frame picker
datePicker = html.Div(
    [   dbc.Row([dbc.Label("Select date range:")]),    
        dcc.DatePickerRange(
        id='timeframepicker',
        min_date_allowed=date(1900, 1, 1),
        max_date_allowed=date.today(),
        initial_visible_month=date(2022, 12, 1),
        start_date=date(2022, 12, 1), #date.today() - datetime.timedelta(2),
        end_date=date(2022, 12, 5) #date.today()
    )
    ],

)

#Dropdown to choose seismic station
dropdown_waveform_filter = html.Div(
    [
        dbc.Label("Filter waveform by:"),
        dcc.Dropdown(
            ['DISP', 'VEL', 'ACC'],
            'ACC',
            id="dropdownwavefilt",
            clearable=False,
        ),
    ],
    className="mb-4",
)

seismic_waveform_filt = dbc.Form([dropdown_seismic_station, datePicker, dropdown_waveform_filter, dbc.Button("Submit", color="primary",
                                        className="mb-3", id = "formsubmitbut")])

seismic_form =  dbc.Card([seismic_waveform_filt],  body=True, style=elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

waveform_data_graph = dbc.Card(dbc.Spinner([html.Div(id="waveformgraph")], color="primary"),  body=True, style=elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)

seismic_row_one = dbc.Row([dbc.Col([seismic_form], width = 4), dbc.Col([waveform_data_graph], width = 8)])

spectrogram_graph = dbc.Card(dbc.Spinner([html.Div(id="spectrogramgraph")], color="primary"),  body=True, style=elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

psd_graph = dbc.Card(dbc.Spinner([html.Div(id="psdgraph")], color="primary"),  body=True, style=elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)

seismic_row_two = dbc.Row([dbc.Col([spectrogram_graph], width =7), dbc.Col([psd_graph],  width =5)])

ALL_SEISMIC_ELEMENTS = [seismic_row_one, seismic_row_two]
