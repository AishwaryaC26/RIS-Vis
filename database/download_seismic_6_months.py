from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client
import obspy

import os
from dotenv import load_dotenv
import ast
import sqlite3
from sqlite3 import Error
from datetime import date, datetime, timedelta
from os.path import exists

## Program to download 6 months of seismic data (to test database capabilities)

load_dotenv()

client = Client('IRIS')
stations = ast.literal_eval(os.environ["SEISMIC_STATIONS"])
#create list of stations from "stations" dict
stationsoptions = list(stations.keys())


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn
        
def nightly_download_mseed_waveform(conn, date_to_download):
    next_day = date_to_download + timedelta(1)
    print(date_to_download)
    file_write = "{}.mseed".format(date_to_download)
    for station in stationsoptions:
        try:
            st = client.get_waveforms(stations[station]["net"], station, stations[station]["loc"], 
                                  stations[station]["chan"], UTCDateTime(date_to_download), UTCDateTime(next_day), attach_response=True)
        except obspy.clients.fdsn.header.FDSNNoDataException as e:
            st = None
        if not st:
            binaryData = "NULL"
        else:
            st.write(file_write, format="MSEED") #download mseed file
            binaryData = convertToBinaryData(file_write)
        '''
        Insert time stamp, BLOB file
        '''
        db_name = "seismic_data"
        query = f"""
        INSERT INTO {db_name} (timestamp, station, mseed)
        VALUES(?, ?, ?);"""
        data_tuple = (date_to_download, station, binaryData)
        cur = conn.cursor()
        cur.execute(query, data_tuple)
    
    conn.commit()
    if exists(file_write):
        os.remove(file_write)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

start = date(2023, 4, 9)
conn = create_connection("database/sqlitedata.db")
for k in range(88):
    nightly_download_mseed_waveform(conn, start)
    start += timedelta(1)
conn.close()