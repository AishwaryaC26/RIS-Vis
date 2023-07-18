from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client
import obspy

import os
from dotenv import load_dotenv
import ast

from datetime import date, datetime, timedelta
import sqlite3
from os.path import exists
import io

load_dotenv()

stations = ast.literal_eval(os.environ["SEISMIC_STATIONS"])
#create list of stations from "stations" dict
stationsoptions = list(stations.keys())


def nightly_download_mseed_waveform():
    ## ACCOUNTING FOR MISSED DOWNLOAD: in case a downloading is missed, we should download everything from the day before
    ## and go back until all gaps are filled.
    print("downloading seismic data...")
    client = Client('IRIS')
    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()
    db_name = "seismic_data"
    writeFile = io.BytesIO()

    ## start date:
    date_to_download = UTCDateTime(date.today() - timedelta(days=1)) ## 3 AM, so you want the day before
    date_today = date.today() - timedelta(days=1) 

    ## checking initial
    check_query = f"""SELECT EXISTS(SELECT * FROM {db_name} WHERE timestamp=?);"""
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

            lines = None
            with open("logs/seismic_log.txt", "r+") as f:
                lines = f.readlines()
                lines = [j.strip() for j in lines if j and j!="\n"]
                if not lines:
                    f.write("Station Date Filename")
                if len(lines) <= 500:
                    lines = None
                elif len(lines) > 500:
                    lines = lines[len(lines) - 150:]
                f.close()
            if lines:
                with open("logs/seismic_log.txt", "w") as sf:
                    sf.write("Station Date Filename")
                    for l in lines:
                        sf.write("\n"+l)
                    sf.close()
            with open("logs/seismic_log.txt", "a") as f:
                if not st: 
                    f.write(f"""\n{station} {str(date.today()).replace('-', '/')} \"{str(date_today).replace('-','/')}.mseed - NA\"""")
                else:
                    f.write(f"""\n{station} {str(date.today()).replace('-', '/')} {str(date_today).replace('-','/')}.mseed""")
                f.close()

            '''
            Insert time stamp, BLOB file
            '''
            query = f"""
            INSERT INTO {db_name} (timestamp, station, mseed)
            VALUES(?, ?, ?);"""
            data_tuple = (str(date_today), station, binaryData)
            cur.execute(query, data_tuple)

        ## keep going until all missed files are accounted for    
        date_today = date_today - timedelta(days=1) 
        date_to_download = UTCDateTime(date_today)

        ## check whether new date is in table
        check_query = f"""SELECT EXISTS(SELECT * FROM {db_name} WHERE timestamp=?);"""
        check_data_tuple = (str(date_today)[:10],)
        cur.execute(check_query, check_data_tuple)
        check_res = cur.fetchall()

    writeFile.close()
    conn.commit()
    conn.close()

def convertToBinaryData(filename):
    # Convert digital data to binary format
    return filename.getvalue()


