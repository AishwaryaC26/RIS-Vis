import pandas as pd
import plotly.express as px
import ast, os
from dotenv import load_dotenv

load_dotenv()

weather_coords = [ast.literal_eval("(-81.5,-175.0)")]

df = pd.DataFrame(weather_coords, columns=['Latitude', 'Longitude'])

fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", zoom=3, height=500)
fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
    ])
fig.update_traces(marker=dict(
    size = 20
),)

fig.show()