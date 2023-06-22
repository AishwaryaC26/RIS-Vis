from obspy.core import UTCDateTime
import time
from obspy.clients.fdsn import Client

client = Client('IRIS')
 


start = time.time()

net = '2H'
sta = 'CONZ'
loc = '--'
chan = 'LHZ'

#setting start time and end time
starttime = UTCDateTime('2022-12-01T00:00:00')
endtime = UTCDateTime('2022-12-05T00:00:00')

st = client.get_waveforms(net, sta, loc, chan, starttime, endtime, attach_response = True)

tr = st[0]
st.write("./backend/IRIS_seismic_data/seismic_files/test.mseed", format="MSEED")  

def nightly_download_mseed_waveform():

    

