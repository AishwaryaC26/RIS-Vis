
"""
MIT Haystack REU Project: Dashboard to track Antarctic Ross Ice Shelf Data
Built by: Aishwarya Chakravarthy
"""
import time
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import obspy

from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client
import pandas as pd

import plotly.express as px
import datetime
from datetime import date

import mpld3     
import matplotlib

matplotlib.use('agg') # prevents matplotlib from plotting 

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
client = Client('IRIS') #establish client to access API


### GLOBAL VARIABLES ###

startdate = date(2022, 1, 1) #change this date to reflect first date of data collection of SGIP
# this date was chosen specifically to test this application with the ELHT station

# IRIS seismic stations
# Add new stations in the following format - 
# Station name: {"net": network, "loc": location, "chan": channel}
### NOTE: format might need to be changed if multiple stations have the same name ###
stations = {"HOO": {"net": "1G", "loc": "--", "chan" : "LHZ"}, 
            "CONZ": {"net": "2H", "loc": "--", "chan": "LHZ"}, 
            "ELHT": {"net": "2H", "loc": "--", "chan": "LHZ"}, 
            "NAUS": {"net": "2H", "loc": "--", "chan": "LHZ"}}

#create list of stations from "stations" dict
stationsoptions = list(stations.keys())

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "25rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

#sidebar component
sidebar = html.Div(
    [
        html.H2("MIT Haystack SGIP Data Visualizer", className="display-4"),
        html.Hr(),
        html.P(
            "Click through the tabs to visualize SGIP data.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Seismic Data", href="/seismic", active="exact"),
                dbc.NavLink("GPS Data", href="/gps", active="exact"),
                dbc.NavLink("Weather Data", href="/weather", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

#content component
content = html.Div(id="page-content", style=CONTENT_STYLE)

#setting up app's layout
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


#all calculative methods

#method to create waveform
def create_waveform_graph(net, sta, chan, starttime, endtime):
    start = time.time()
    # query for data
    try: 
        st = client.get_waveforms(net, sta, '--', chan, starttime, endtime, attach_response = True)
    except obspy.clients.fdsn.header.FDSNNoDataException as e:
        st = None
        return [st, px.line()]
    waveformdata = st[0].data
    waveformtimes = st[0].times(type="relative")
    waveformtimes = [tr/86400 for tr in waveformtimes]
    
    df = pd.DataFrame({
        'Time (in days)': waveformtimes, 
        'Amplitude': waveformdata,
    })

    fig = px.line(df, x="Time (in days)", y="Amplitude",render_mode='webgl')
    print(time.time() - start)
    return [st, fig]

#def apply_filter(df, freq, corners):

def create_spectrogram(currentwave):
    #using currentwave variable- which represents the current waveform user is examining
    if not currentwave:
        return "No Data Found"
    return mpld3.fig_to_html(currentwave.spectrogram(show=False)[0])



#Seismic Page Components

#Introduction to Seismic Page
seismic_introduction = dbc.Container(
    [
        html.H3("Seismic Data", className="display-5"),
        html.P(
            "Use the below features to examine waveform data and generate spectograms.",
            className="lead",
        ), 
         html.P(
            "It is recommended to choose time periods that do not last" + 
            " longer than a month. If an empty graph is displayed, data is not available for the time period chosen.",
            className="lead",
        )
    ],
    fluid=True,
    className="py-3",
)


#Dropdown to choose seismic station
dropdown = html.Div(
    [
        dbc.Label("Select seismic station:"),
        dcc.Dropdown(
            stationsoptions,
            stationsoptions[0],
            id="dropdownseismic",
            clearable=False,
        ), 
    ],
    className="mb-4",
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
     className="mb-4",
)

#waveform filter settings 
pickfilter = html.Div([
        html.Hr(),
        dbc.Label("Waveform filters:"), 
        dbc.InputGroup(
            [
                dbc.Select(
                    options=[
                        {"label": 'None', "value": 'None'},
                        {"label": 'bandpass', "value": 'bandpass'},
                        {"label": 'bandstop', "value": 'bandstop'},
                        {"label": 'lowpass', "value": 'lowpass'},
                        {"label": 'highpass', "value": 'highpass'},
                    ], id = "filterselect", value="None"
                ),
            ]
        ),
        html.Div([
        html.Br(),
        dbc.Label("Filter settings:"),

        dbc.InputGroup(
            [dbc.InputGroupText("Minimum Frequency", id = "minfreqtext"), dbc.Input(placeholder="0.1", type = "number", id = "minfreqinput"), 
            dbc.FormFeedback("Please input a value.", type="invalid",),],
            className="mb-3",
        ),
        dbc.InputGroup(
            [dbc.InputGroupText("Maximum Frequency"), dbc.Input(placeholder="0.1", type = "number", id = "maxfreqinput"), dbc.FormFeedback("Please input a value.", type="invalid",),],
            className="mb-3",
            id = "maxfreq"
        ),
        dbc.InputGroup(
            [ dbc.InputGroupText("Sampling Rate"), dbc.Input(placeholder="5", type = "number", id = "samplingrateinput"), dbc.FormFeedback("Please input a value.", type="invalid",),],
            className="mb-3",
        ),
        dbc.InputGroup(
            [dbc.InputGroupText("Corners"), dbc.Input(placeholder="4", type = "number", id = "cornersinput"), dbc.FormFeedback("Please input a value.", type="invalid",),],
            className="mb-3",
        ), 
         dbc.InputGroup(
            [
                dbc.InputGroupText("Zerophase"),
                dbc.Select(
                    options=[
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ], value="No"
                ),
            ]
        ),
    ],
            hidden=True,
            id="filtersettingsdiv",
            className="mb-4",
        )
    ]
)


#callback so that filter settings only pops up when filter is chosen 
@app.callback(
        Output("filtersettingsdiv", "hidden"),
        Output("maxfreq", "hidden"),
        Output("minfreqtext", "value"),
        Input("filterselect", "value"),
)
def update_filter_form(value):
    retthis = "Maximum Frequency"
    if value == "highpass" or value == "lowpass":
        retthis = "Corner Frequency"
    return value == "None" or value == None, value == "highpass" or value == "lowpass", retthis 

spectrogramfilters = html.Div([
    html.Hr(),
    dbc.Label("Spectogram Filters:"),
    dbc.InputGroup(
            [
                dbc.InputGroupText("Log"),
                dbc.Select(
                    options=[
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ],  value="No"
                ),
            ], 
            className="mb-3",
        ), 
    dbc.InputGroup(
            [
                dbc.InputGroupText("Dbscale"),
                dbc.Select(
                    options=[
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ], value="No"
                ),
            ], 
            className="mb-3",
        ),
])

#creating a form with all of the inputs
controls = dbc.Card([dbc.Form( [dropdown, datePicker, pickfilter, spectrogramfilters, dbc.Button("Submit", color="primary", 
                                        className="mb-3", id = "formsubmitbut", disabled=True)])], body = True)


#callbacks to check that all inputs are present when submit is pressed
@app.callback(
    Output("minfreqinput", "invalid"),
    Output("maxfreqinput", "invalid"),
    Output("samplingrateinput", "invalid"),
    Output("cornersinput", "invalid"),
    Input("minfreqinput", "value"),
    Input("maxfreqinput", "value"),
    Input("samplingrateinput", "value"),
    Input("cornersinput", "value"),
)
def check_incorrect_input(minfreq, maxfreq, samplingrate, corners):
    return not minfreq, not maxfreq, not samplingrate, not corners


#callback for submit button
@app.callback(
    Output("formsubmitbut", "disabled"),
    Input("minfreqinput", "value"),
    Input("maxfreqinput", "value"),
    Input("samplingrateinput", "value"),
    Input("cornersinput", "value"),
    Input("filterselect", "value"), 
)
def make_submit_visible(minfreqinput, maxfreqinput, samplingrateinput, cornersinput, filterselect):
    if filterselect=="None":
        return False
    elif filterselect == "lowpass" or filterselect == "highpass":
        return not (minfreqinput and samplingrateinput and cornersinput and filterselect)
    if minfreqinput and maxfreqinput and samplingrateinput and cornersinput and filterselect:
        return False
    return True 

waveform_graph = dbc.Card([html.H3("Waveform"), dcc.Loading(
    children=[dcc.Graph(id="waveformgraph"),],
    type="circle")], body = True, )

spectogram_graph = dbc.Card([html.H3("Spectrogram"), dcc.Loading(
                children = [html.Iframe(
                id='spectrogram', srcDoc=None,  
                style={'border-width': '5', 'width': '100%',
                       'height': '500px'})], type="circle"  
                )], body = True, style={"width": "50%"})

tabs = dbc.Card([html.H3("Waveform Data", className="display-6"), 
                 dcc.Loading(
                children=[dcc.Graph(id="waveformgraph"),],
                type="circle"), 
                
                dcc.Loading(
                children = [html.Iframe(
                id='spectrogram', srcDoc=None,  
                style={'border-width': '5', 'width': '100%',
                       'height': '500px'})], type="circle"  
                )], body=True,)

#callback to use date-picker and station selection to create graph
@app.callback(
        Output("waveformgraph", "figure"),
        Output("spectrogram", "srcDoc"),
        Input("timeframepicker", "start_date"),
        Input("timeframepicker", "end_date"),
        Input("dropdownseismic", "value")
)
def update_seismometer_graph(start_date, end_date, dropdownvalue):
    start_date = UTCDateTime(start_date + 'T00:00:00')
    end_date = UTCDateTime(end_date + 'T00:00:00')
    results = create_waveform_graph(stations[dropdownvalue]["net"], dropdownvalue, stations[dropdownvalue]["chan"], start_date, end_date)
    return results[1], create_spectrogram(results[0])


#page callback- establishes different pages of website
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("Oh cool, this is the home page!")
    elif pathname == "/seismic":
        return html.Div(children=[
            seismic_introduction,
            controls, 
            html.Br(), 
            waveform_graph,
            html.Br(), 
            spectogram_graph,
        ])
    elif pathname == "/gps":
        return html.P("Oh cool, this is page 2!")
    elif pathname == "/weather":
        return html.P("Oh cool, this is the weather page!")
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


if __name__ == "__main__":
    app.run_server(debug=True)

'''import numpy as np
import obspy

from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd


# Initialize the app
app = Dash(__name__)

client = Client('IRIS')
net = '2H'
sta = 'CONZ'
loc = '--'
chan = 'LHZ'

#setting start time and end time
starttime = UTCDateTime('2022-12-01T00:00:00')
endtime = UTCDateTime('2022-12-03T00:00:00')

# query for data
st = client.get_waveforms(net, sta, loc, chan, starttime, endtime, attach_response = True)

st_flt = st.copy()
st_flt = st_flt.filter('bandpass', freqmin = 0.001, freqmax = 0.1)

st_disp = st_flt.copy()
#st_disp = st_disp.remove_response(output = "DISP") 

tr = st_disp[0]
waveformdata = tr.data
waveformtimes = tr.times(type="utcdatetime")

df = pd.DataFrame({
    'times': waveformtimes, 
    'Data': waveformdata
})


fig = px.line(df, x="times", y="Data", title='Waveform Data')

app.layout = html.Div(children=[
    html.H1(children='Test Seismic Data'),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
'''
