import sqlite3
import pandas as pd
import plotly.express as px

def get_gps_tracks(start_date, end_date):
    conn = sqlite3.connect("database/sqlitedata.db")
    cur = conn.cursor()

    query = f"""SELECT timestamp, station, currlatitude, 
    currlongitude, currheight FROM gps_data WHERE timestamp >= ? AND timestamp <= ?; """
    query_inputs = (start_date, end_date)

    cur.execute(query, query_inputs)
    all_results = cur.fetchall()
    if all_results:
        df = pd.DataFrame(all_results, columns=['Timestamp', 'Station', 'Latitude', 'Longitude', 'Height'])

        fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", animation_frame="Timestamp", animation_group="Station", hover_name="Station", hover_data=["Timestamp", "Height"], color = "Station",
                            zoom=3, height=500)
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
        fig.update_geos(fitbounds="locations")
        fig.update_traces(marker=dict(
            size = 20
        ),)
        fig.show()

get_gps_tracks("2007-01-01", "2008-01-01")