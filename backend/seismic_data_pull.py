from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client
import obspy

import os
from dotenv import load_dotenv
import ast

from datetime import date, timedelta
import sqlite3
import io
import logmethods


load_dotenv()
stations = ast.literal_eval(os.environ["SEISMIC_STATIONS"])

#create list of stations from "stations" dict
stationsoptions = list(stations.keys())
database_name = os.environ["DATABASE_NAME"]
seismic_table = os.environ["SEISMIC_TABLE_NAME"]
seismic_log = os.environ["SEISMIC_LOG_LOC"]

print("seismic db", database_name)
print("seismic table", seismic_table)
print("seismic log", seismic_log)

def nightly_download_mseed_waveform():
    ## ACCOUNTING FOR MISSED DOWNLOAD: in case a download is missed, method downloads everything from the day before
    ## and go back until all gaps are filled.
    print("downloading seismic data...")
    client = Client('IRIS')
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    table_name = seismic_table
    writeFile = io.BytesIO()

    ## start date:
    date_to_download = UTCDateTime(date.today() - timedelta(days=1)) ## 3 AM, so you want the day before
    date_today = date.today() - timedelta(days=1) 

    ## checking initial
    check_query = f"""SELECT EXISTS(SELECT * FROM {table_name} WHERE timestamp=?);"""
    check_data_tuple = (str(date_today)[:10],)
    cur.execute(check_query, check_data_tuple)
    check_res = cur.fetchall()

    while check_res[0][0] == 0:
        next_day = date_to_download + 1 ##getting next day 
        print(date_to_download, flush = True)
        for station in stationsoptions:
            try:
                st = client.get_waveforms(stations[station]["net"], station, stations[station]["loc"], 
                                    stations[station]["chan"], UTCDateTime(date_to_download), UTCDateTime(next_day), attach_response=True)
            except obspy.clients.fdsn.header.FDSNNoDataException as e:
                st = None
            if not st:
                binaryData = "NULL"
            else:
                writeFile.seek(0)
                writeFile.truncate()
                st.write(writeFile, format="MSEED") #download mseed file
                binaryData = convertToBinaryData(writeFile)

            if not st:
                new_line = f"""\n{station} {str(date.today()).replace('-', '/')} \"{str(date_today).replace('-','/')}.mseed - NA\""""
            else:
                new_line = f"""\n{station} {str(date.today()).replace('-', '/')} {str(date_today).replace('-','/')}.mseed"""

            logmethods.write_to_log(seismic_log, "Station Download-Date Filename", new_line)
        
            '''
            Insert time stamp, BLOB file
            '''
            query = f"""
            INSERT INTO {table_name} (timestamp, station, mseed)
            VALUES(?, ?, ?);"""
            data_tuple = (str(date_today), station, binaryData)
            cur.execute(query, data_tuple)

        ## keep going until all missed files are accounted for    
        date_today = date_today - timedelta(days=1) 
        date_to_download = UTCDateTime(date_today)

        ## check whether new date is in table
        check_query = f"""SELECT EXISTS(SELECT * FROM {table_name} WHERE timestamp=?);"""
        check_data_tuple = (str(date_today)[:10],)
        cur.execute(check_query, check_data_tuple)
        check_res = cur.fetchall()

    writeFile.close()
    conn.commit()
    conn.close()

def convertToBinaryData(filename):
    # Convert digital data to binary format
    return filename.getvalue()



