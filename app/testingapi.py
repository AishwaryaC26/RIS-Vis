import numpy as np
import obspy

from obspy.core import UTCDateTime
from obspy.clients.fdsn import Client

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

import time
import matplotlib.pyplot as plt
import mpld3
from obspy.signal import PPSD
from skimage import io

import plotly.express as px
from skimage import io
img = io.imread('ppsd.png')
fig = px.imshow(img)
fig.show()

'''
start = time.time()
client = Client('IRIS')
net = '2H'
sta = 'CONZ'
loc = '--'
chan = 'LHZ'

#setting start time and end time
starttime = UTCDateTime('2022-12-01T00:00:00')
endtime = UTCDateTime('2022-12-05T00:00:00')
img = io.imread('ppsd.png')
print(img)

# query for data
st = client.get_waveforms(net, sta, loc, chan, starttime, endtime, attach_response = True)
inv = client.get_stations(network=net,station= sta, location=loc, channel=chan, starttime=starttime, endtime=endtime, level = "response")

tr = st[0]
ppsd = PPSD(tr.stats, metadata=inv)
ppsd.add(st)
ppsd.plot(show=False)
plt.savefig('ppsd.png') '''
'''
tr2 = st.copy()
tr2.filter('bandpass', freqmin=0.04, freqmax=0.07, corners=1, zerophase=True)
tr2.plot()


tr3 = st.copy()
tr3.filter('bandpass', freqmin=0.04, freqmax=0.07, corners=4, zerophase=True)
tr3.plot()


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

'''
#creating spectrogram
