import numpy as np
import obspy

from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

import time
import vaex

start = time.time()
client = Client('IRIS')
net = '2H'
sta = 'CONZ'
loc = '--'
chan = 'LHZ'

#setting start time and end time
starttime = UTCDateTime('2022-12-01T00:00:00')
endtime = UTCDateTime('2022-12-25T00:00:00')


# query for data
st = client.get_waveforms(net, sta, loc, chan, starttime, endtime, attach_response = True)
print(time.time() - start)

tr = st[0]
waveformdata = tr.data
waveformtimes = tr.times(type="relative")
# waveformtimes = [tr/86400 for tr in waveformtimes]
# extracting the utc date time is what's taking so long
print(time.time() - start)

df = pd.DataFrame({
    'times': waveformtimes, 
    'Data': waveformdata
})

print(time.time() - start)

fig = px.line(df, x="times", y="Data", title='Waveform Data', render_mode='webgl')
print(time.time() - start)
