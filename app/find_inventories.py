import os
from dotenv import load_dotenv
import ast
from obspy.clients.fdsn import Client

## finds and saves all inventories for seismic stations
load_dotenv()
stations = ast.literal_eval(os.environ["SEISMIC_STATIONS"])

#create list of stations from "stations" dict
stationsoptions = list(stations.keys())

client = Client('IRIS') #establish client to access API

## inventories are stored in "station_inventories" folder in same directory
for sta in stationsoptions:
    inventory = client.get_stations(network=stations[sta]['net'],station= sta, channel=stations[sta]['chan'], location = '--', level = "response")
    inventory.write(f"""{sta}.xml""", format = "STATIONXML")