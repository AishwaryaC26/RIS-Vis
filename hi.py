from geographiclib.geodesic import Geodesic
import ast, os
import sqlite3
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
load_dotenv()


def get_baseline_graphs(start_date, end_date, ref_station):
    from geographiclib.geodesic import Geodesic
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

    for other_stats in other_station_locs:
        ll = other_station_locs[other_stats]
        for row in ll:
            if row[0] in ref_station_dict:
                resultDict = Geodesic.WGS84.Inverse(row[2], row[3], ref_station_dict[row[0]][1], ref_station_dict[row[0]][2])
                df_distance["Time"].append(row[0])
                df_distance["Distance"].append(resultDict["s12"])
                df_distance["Station"].append(other_stats)

                df_orient["Time"].append(row[0])
                df_orient["Angle (in degrees)"].append(resultDict["azi1"])
                df_orient["Station"].append(other_stats)
    

    df_distance = pd.DataFrame(df_distance)
    df_orient = pd.DataFrame(df_orient)

    fig = px.line(df_distance, x="Time", y="Distance", color="Station")
    
    fig.show()
get_baseline_graphs("1995-01-01", "2023-07-15", "FTP4")