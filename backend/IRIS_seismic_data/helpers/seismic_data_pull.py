from obspy.core import UTCDateTime
import time
from obspy.clients.fdsn import Client
import obspy

import os
from dotenv import load_dotenv
import ast

from datetime import date, datetime, timedelta

load_dotenv()

client = Client('IRIS')
stations = ast.literal_eval(os.environ["STATIONS"])
#create list of stations from "stations" dict
stationsoptions = list(stations.keys())

'''
code to calculate time difference between today and start date
startdate = os.environ["START_DATE"]
start_date_obj = datetime.strptime(startdate, '%m-%d-%Y').date()
print(date.today() - start_date_obj)
'''

time_constant = int(os.environ["TIME_CONSTANT"])

def nightly_download_mseed_waveform():
    date_to_download = UTCDateTime(date.today() - timedelta(time_constant + 1))
    next_day = date_to_download + 1
    print(date_to_download)
    for station in stationsoptions:
        try:
            st = client.get_waveforms(stations[station]["net"], station, stations[station]["loc"], 
                                  stations[station]["chan"], date_to_download, next_day, attach_response=True)
        except obspy.clients.fdsn.header.FDSNNoDataException as e:
            continue
        tr = st[0]
        st.write("/backend/IRIS_seismic_data/downloaded_files/{}/{}.mseed".format(station, date_to_download), format="MSEED") # location in Docker container
        


