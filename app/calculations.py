# Plotly Dash related imports
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
import dash_bootstrap_components as dbc

# Obspy related imports
from obspy.signal import PPSD
from obspy.core import UTCDateTime
from  obspy.core.stream import Stream
from obspy.core.trace import Trace
from obspy import read_inventory, read

# Pandas/Numpy/Matplotlib related imports
import pandas as pd
import matplotlib
import matplotlib.mlab as mlab
import numpy as np

# Datetime related imports
from datetime import date, timedelta, datetime

# Database related imports
import sqlite3

# Environment variables related imports
from dotenv import load_dotenv
import ast, os

# Miscellaneous imports
import xarray as xr
import datashader as ds
from datashader import reductions as rd
import io
from geographiclib.geodesic import Geodesic

matplotlib.use('agg') # prevents matplotlib from plotting (might be useful in obspy methods)
load_dotenv()

### ALL CALCULATIVE METHODS REQUIRED ###

### SEISMIC PAGE CALCULATION METHODS ###

#Writes data to file-like object
def writeTofile(data, file):
    file.seek(0)
    file.truncate()
    file.write(data)

# pulls all seismic data corresponding to a specific station, starttime, and endtime
def check_database(sta, starttime, endtime):
    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()

    query = f"""SELECT timestamp, mseed FROM seismic_data WHERE timestamp >= ? AND timestamp <= ? AND station == ?;"""
    query_inputs  = (starttime[:10], endtime[:10], sta)
    cur.execute(query, query_inputs)
    all_results = cur.fetchall()

    conn.close()
    return all_results

'''
Given list of rows pulled from seismic_data database containing
(timestamp, miniSeed data), creates an Obspy stream object
'''
def create_stream(databres):
    st = Stream() ##creates new stream object
    trace = Trace() ##creates new trace object

    # go through all_results, reading each file and adding it to the stream
    waveFile = io.BytesIO()
    for k in databres:
        if k[1] != "NULL":
            writeTofile(k[1], waveFile)
            if trace:
                trace += read(waveFile)[0]
            else: 
                trace = read(waveFile)[0]
    if not len(trace):
        return None
    st.append(trace)
    return st

#creates Waveform graph 
def create_waveform_graph(net, sta, chan, starttime, endtime, extract, fig):
    # query for data from database
    all_results = check_database(sta, starttime, endtime)

    #creates Obspy inventory object
    inventory = read_inventory(f"""station_inventories/{sta}.xml""")

    if all_results:
        st = create_stream(all_results)
        if not st:
            return dbc.Label("No data was found."), None, None
    else:
        return dbc.Label("No data was found."), None, None  
    
    ret = st.copy()
    filtered_data = st.remove_response(output = extract, inventory = inventory) ## filter stream based on filter option selected
    waveformdata = filtered_data[0].data
    waveformtimes = filtered_data[0].times(type="relative")
   
    df = pd.DataFrame({
        'Time (in days)': waveformtimes,
        'Amplitude': waveformdata,
    })

    fig.add_trace(
        go.Scattergl(
            x = df['Time (in days)'],
            y = df['Amplitude'],
            )
    )
    
    fig.update_layout(
    title="Waveform Data",
    xaxis_title="Time (s)",
    yaxis_title=" ",
    )
    
    fig.update_layout(template='plotly_dark')
    return  [dcc.Graph(figure = fig, id = "waveformgraphgr"), ret, inventory]


## method to create PSD given Obspy Stream object and Inventory object corresponding to the stream
def create_psd(currWaveForm, currInventory):
    if not currWaveForm:
        return dbc.Label("No data was found.")
    
    tr = currWaveForm[0]
    ppsd = PPSD(tr.stats, metadata=currInventory)
    ppsd.add(currWaveForm)

    ## gets mode value of all predicted PSDs
    mode_psd = ppsd.get_mode()
    frequencies = [1/x for x in mode_psd[0]]

    fig = go.Figure(data=go.Scatter(x=frequencies, y=mode_psd[1]))
    x_min, x_max = min(frequencies), max(frequencies)
    y_min, y_max = min(mode_psd[1]) - 25, max(mode_psd[1]) + 25
    fig.update_xaxes(range=[x_min, x_max])
    fig.update_yaxes(range=[y_min, y_max]) 
    fig.update_layout(template='plotly_dark')

    fig.update_layout(
    title="Power Spectral Density",
    xaxis_title='Frequency (Hz)',
    yaxis_title='Amplitude (dB)',
    )
    return dcc.Graph(figure = fig)


## method to create spectrogram given Obspy Stream object
def create_spectrogram(currWaveForm):
    if not currWaveForm:
        return dbc.Label("No data was found.")
    
    data = currWaveForm[0].data
    samp_rate = float(currWaveForm[0].stats.sampling_rate)

    data = data - data.mean()
    spectrum, freqs, t = mlab.specgram(data, Fs = samp_rate, NFFT=512)
    spectrum = np.sqrt(spectrum[1:, :])
    freqs = freqs[1:]
    
    ## downsamples the data to 800 pixels so Plotly can display
    pw_s = xr.DataArray(spectrum, coords=[('Frequency (Hz)', freqs), ('Time (s)', t)])
    cvs = ds.Canvas(plot_width=800, plot_height=300,
                x_range=(t[0], t[-1]),
                y_range=(freqs[0], freqs[-1]))
    
    agg = cvs.raster(pw_s, agg=rd.mean())
    fig = px.imshow(agg, 
                    origin="lower", )
    
    fig.update_layout(
    title="Spectrogram",
    xaxis_title='Time (s)',
    yaxis_title='Frequency (Hz)',
    )
    fig.update_layout(template='plotly_dark')
    retGraph = dcc.Graph(figure = fig)
    return retGraph


### WEATHER PAGE CALCULATION METHODS ###

#creates weather temperature, pressure, and relative humidity graphs given start date and end date

def create_weather_graphs(starttime, endtime):
    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()

    query = f"""SELECT timestamp, temperature, pressure, relhumidity 
    FROM weather_data WHERE timestamp >= ? AND timestamp <= ?; """
    query_inputs  = (starttime, endtime)
    cur.execute(query, query_inputs)
    all_results = cur.fetchall()

    if not all_results:
        return dbc.Label("No data was found."), dbc.Label("No data was found."), dbc.Label("No data was found.")
    
    times, temp, pressure, relhum = [], [], [], []

    ### 444 represents No Data Available
    ## so - rows that have 444 will not be included in graphs
    for res in all_results:
        if (res[1] != 444 and res[2] != 444 and res[3] != 444):
            times.append(res[0])
            temp.append(res[1])
            pressure.append(res[2])
            relhum.append(res[3])

    df = pd.DataFrame({
        'Time': times,
        'Pressure': pressure, 
        'Relative Humidity': relhum, 
        'Temperature': temp
    })

    temp_fig = go.Figure()
    temp_fig.add_trace(
        go.Scattergl(
            x = df['Time'],
            y = df['Temperature'],
            )
    )

    temp_fig.update_layout(
    title="Temperature",
    xaxis_title="Time",
    yaxis_title="Temperature (C)",
    )

    press_fig = go.Figure()
    press_fig.add_trace(
        go.Scattergl(
            x = df['Time'],
            y = df['Pressure'],
            )
    )

    press_fig.update_layout(
    title="Pressure",
    xaxis_title="Time",
    yaxis_title="Press",
    )


    relhum_fig = go.Figure()
    relhum_fig.add_trace(
        go.Scattergl(
            x = df['Time'],
            y = df['Relative Humidity'],
            )
    )

    relhum_fig.update_layout(
    title="Relative Humidity",
    xaxis_title="Time",
    yaxis_title="Rel. Hum.",
    )


    temp_fig.update_layout(template='plotly_dark')
    press_fig.update_layout(template='plotly_dark')
    relhum_fig.update_layout(template='plotly_dark')
    conn.close()
    return dcc.Graph(figure = temp_fig), dcc.Graph(figure = press_fig), dcc.Graph(figure = relhum_fig)

### GPS PAGE CALCULATION METHODS ###

# Creates GPS graphs of east, north, and up movement given starttime, endtime, & station
def create_gps_graphs(starttime, endtime, station):
    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()
    query = f"""SELECT timestamp, eastingsf, northingsf, verticalf 
    FROM gps_data WHERE timestamp >= ? AND timestamp <= ? AND station = ?; """
    query_inputs  = (starttime, endtime, station)
    cur.execute(query, query_inputs)
    all_results = cur.fetchall()

    if not all_results:
        return dbc.Label("No data was found."), dbc.Label("No data was found."), dbc.Label("No data was found.")
    
    times, east, north, up = [], [], [], []
    for res in all_results:
        times.append(res[0])
        east.append(res[1])
        north.append(res[2])
        up.append(res[3])

    df = pd.DataFrame({
        'Time': times,
        'East': east, 
        'North': north, 
        'Up': up
    })

    east_fig = go.Figure()
    east_fig.add_trace(
        go.Scattergl(
            x = df['Time'],
            y = df['East'],
            )
    )

    east_fig.update_layout(
    title="East Movement",
    xaxis_title="Date",
    yaxis_title="East (m)",
    )


    north_fig = go.Figure()
    north_fig.add_trace(
        go.Scattergl(
            x = df['Time'],
            y = df['North'],
            )
    )

    north_fig.update_layout(
    title="North Movement",
    xaxis_title="Date",
    yaxis_title="North (m)",
    )

    up_fig = go.Figure()
    up_fig.add_trace(
        go.Scattergl(
            x = df['Time'],
            y = df['Up'],
            )
    )

    up_fig.update_layout(
    title="Up Movement",
    xaxis_title="Date",
    yaxis_title="Up (m)",
    )

    east_fig.update_layout(template='plotly_dark')
    north_fig.update_layout(template='plotly_dark')
    up_fig.update_layout(template='plotly_dark')

    conn.close()
    return dcc.Graph(figure = east_fig), dcc.Graph(figure = north_fig), dcc.Graph(figure = up_fig)

### HOME PAGE CALCULATION METHODS ###

## creates spectogram of seismic data from last 5 days
def create_spec_five_days(station):
    starttime = str(date.today() - timedelta(days=365))[:10]
    endtime = str(date.today() - timedelta(days=360))[:10]
    #starttime = str(date.today() - timedelta(days=5))[:10]
    #endtime = str(date.today())[:10]
    all_results = check_database(station, starttime, endtime)
    if not all_results:
        return dbc.Label("No data was found")
    stream = create_stream(all_results)
    if not stream:
        return dbc.Label("No data was found")
    return create_spectrogram(stream)

# creates PSD of seismic data from last 5 days
def create_psd_five_days(station):
    starttime = str(date.today() - timedelta(days=365))[:10]
    endtime = str(date.today() - timedelta(days=360))[:10]
    #starttime = str(date.today() - timedelta(days=5))[:10]
    #endtime = str(date.today())[:10]
    all_results = check_database(station, starttime, endtime)
    if not all_results:
        return dbc.Label("No data was found")
    stream = create_stream(all_results)
    if not stream:
        return dbc.Label("No data was found")
    inventory = read_inventory(f"""station_inventories/{station}.xml""")
    return create_psd(stream, inventory)

## reads log files
def read_file(file_name, type = "NA"):
    with open(file_name) as f:
        lines = f.readlines()
        if not lines:
            return "No files have been downloaded"
    log = pd.read_csv(file_name, delim_whitespace=True)
    last_10 = log.tail(10)
    return dbc.Table.from_dataframe(last_10, striped=True, bordered=True,  hover=True,
    responsive=True,)

### GPS Visualizations Page Calculation Methods ###

def get_gps_loc(start_date, end_date, station):
    ## let us evaluate in a period of months 
    objstart_date = datetime.strptime(start_date, "%Y-%m-%d")
    objend_date = datetime.strptime(end_date, "%Y-%m-%d")
    timedif = int((objend_date - objstart_date).days / 50) + 1
    all_dates = [str(objstart_date)]
    while objstart_date < objend_date:
        objstart_date += timedelta(days = timedif)
        all_dates.append(str(objstart_date))
    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()
    query = f"""SELECT timestamp, station, eastingsf, northingsf, verticalf
    FROM gps_data WHERE timestamp IN {str(tuple(all_dates))} AND station = ?; """
    query_inputs  = (station, )
    cur.execute(query, query_inputs)
    all_results = cur.fetchall()
    if not all_results:
        ## check if there's any data at all
        query = f"""SELECT timestamp, station, eastingsf, northingsf, verticalf
        FROM gps_data WHERE timestamp >= ? AND timestamp <= ? AND station = ?; """
        query_inputs  = (start_date, end_date, station, )
        cur.execute(query, query_inputs)
        all_results = cur.fetchall()
        if not all_results:
                return dbc.Label("No data was found.")
        elif len(all_results) > 500:
            dbc.Label("Too much data to display. Please select a smaller time frame.")
    df = pd.DataFrame(all_results, columns=['Date', 'Station', 'East', 'North', 'Vertical'])
    df['East'] *= 100 ## so units will be in mm    
    fig = px.scatter(df, x="East", y="North", animation_frame="Date", animation_group="Station",
    range_x=[min(df["East"]),max(df["East"])], range_y=[min(df["North"]),max(df["North"])], hover_name="Date", hover_data=["Vertical"],
    )
    fig.update_traces(marker=dict(
            size = 20
        ),)
    fig.update_layout(template='plotly_dark')
    conn.close()
    return dcc.Graph(figure = fig)

def get_baseline_graphs(start_date, end_date, ref_station):
    gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])

    query = f"""SELECT timestamp, station, currlatitude, currlongitude, currheight
        FROM gps_data WHERE timestamp >= ? AND timestamp <= ? AND station = ?; """
    
    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()

    ##first get all data from reference station
    query_inputs = (start_date, end_date, ref_station)
    cur.execute(query, query_inputs)

    ref_station_locations = cur.fetchall()
    ## create a dictionary for fast accesstimes
    ref_station_dict = {}
    for row in ref_station_locations:
        ref_station_dict[row[0]] = [row[1], row[2], row[3], row[4]]

    other_station_locs = {}
    for station in gps_stations:
        if station != ref_station:
            query_inputs = (start_date, end_date, station)
            cur.execute(query, query_inputs)
            other_station_locs[station] = cur.fetchall()
    
    
    ## now you have a dict containing locations of other stations
    ## go through and create dataframes for plotting

    df_distance = {'Time': [], 'Distance': [], 'Station': []}
    df_orient = {'Time': [], 'Angle (in degrees)': [], 'Station': []}
    ## stores how much to subtract for each station
    df_distance_resid = {'Time': [], 'Distance': [], 'Station': []}
    df_orient_resid = {'Time': [], 'Angle (in degrees)': [], 'Station': []}


    for other_stats in other_station_locs:
        ll = other_station_locs[other_stats]
        firstpassed = False
        subdist = -1
        subang = -1
        for row in ll:
            if row[0] in ref_station_dict:
                resultDict = Geodesic.WGS84.Inverse(row[2], row[3], ref_station_dict[row[0]][1], ref_station_dict[row[0]][2])
                df_distance["Time"].append(row[0])
                df_distance["Distance"].append(resultDict["s12"])
                df_distance["Station"].append(other_stats)

                df_orient["Time"].append(row[0])
                df_orient["Angle (in degrees)"].append(resultDict["azi1"])
                df_orient["Station"].append(other_stats)

                df_distance_resid["Time"].append(row[0])
                df_distance_resid["Station"].append(other_stats)
                df_orient_resid["Time"].append(row[0])
                df_orient_resid["Station"].append(other_stats)

                if not firstpassed:
                    firstpassed = True
                    subdist = resultDict["s12"]
                    subang = resultDict["azi1"]
                    df_distance_resid["Distance"].append(0)
                    df_orient_resid["Angle (in degrees)"].append(0)
                else:
                    df_distance_resid["Distance"].append(resultDict["s12"] - subdist)
                    df_orient_resid["Angle (in degrees)"].append(resultDict["azi1"] - subang)

      
    df_distance = pd.DataFrame(df_distance)
    df_orient = pd.DataFrame(df_orient)

    if df_distance.empty:
        return dbc.Label("No data was found."), dbc.Label("No data was found."), dbc.Label("No data was found."), dbc.Label("No data was found.")

    fig_distance = px.line(df_distance, x="Time", y="Distance", color="Station")
    fig_orient = px.line(df_orient, x="Time", y="Angle (in degrees)", color="Station")


    df_distance_residual = pd.DataFrame(df_distance_resid)
    df_orient_residual = pd.DataFrame(df_orient_resid)

    fig_distance_residual = px.line(df_distance_residual, x="Time", y="Distance", color="Station")
    fig_orient_residual = px.line(df_orient_residual, x="Time", y="Angle (in degrees)", color="Station")

   

    fig_distance.update_layout(template='plotly_dark')
    fig_orient.update_layout(template='plotly_dark')
    fig_distance_residual.update_layout(template='plotly_dark')
    fig_orient_residual.update_layout(template='plotly_dark')
     
    return dcc.Graph(figure = fig_distance), dcc.Graph(figure = fig_orient), dcc.Graph(figure = fig_distance_residual), dcc.Graph(figure = fig_orient_residual)