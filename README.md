# RIS-Vis: MIT Haystack SGIP Data Monitor and Visualizer

Built by Aishwarya Chakravarthy (MIT Haystack REU 2023)

## Table of contents
- Introduction
- Requirements
- Technologies Used
- Installation
- Detailed Description
- Database Schema
- Customization
- Future Steps

## Introduction
RIS-Vis is a web dashboard application built with the purpose of helping visualize seismic, geodetic, weather, & system monitoring data from the Seismo-Geodetic Ice Penetrator (SGIP) built by the MIT Haystack Observatory. The SGIP is an instrument with seismic and geodetic sensors embedded that will collect data from the Ross Ice Shelf (in Antarctica) when deployed. Since there is currently no data from the SGIP available (as it has not been launched yet), the web application in this repository uses a variety of publicly available data from the IRIS DMC, the Nevada Geodetic Laboratory, & the University of Wisconsin-Madison Automatic Weather Station database. These sources respectively collect seismic, geodetic, and weather data from locations around Antarctica/the rest of the world, including the Ross Ice Shelf. Features of the dashboard include visualizing spectrograms, power spectral densities, GPS station plots, and many more!

## Requirements
To run RIS-Vis on your computer, it is necessary to have Docker installed. Please follow the instructions at https://docs.docker.com/get-docker/ to install Docker on your computer.

## Technologies Used
RIS-Vis was built using Python for the front-end and SQLite3 for the backend database. Specifically, the front-end was built using the Plotly Dash web framework, popularly used for creating interactive data visualizations. 

## Installation
To build RIS-Vis on your own computer:
- Go to your terminal & run <code> git clone https://github.mit.edu/barrettj/achakrav_reu2023.git</code> into your preferred location
- Then, within terminal, go to the directory with the repository
- Run <code> docker-compose up --build </code>
- The web application should run at http://localhost:8080/!

To stop running RIS-Vis:
-  Run the command "docker-compose down" on terminal in the project folder directory
-  To restart the project again, you can simply call "docker-compose up --build"

## Detailed Description
RIS-Vis was built with an emphasis on making it simple to add/remove components!

Before we discuss how to add/remove components, let's take a tour of the repository:

Here is the layout of the app section of the repository --> 

```bash 
app
├── Dockerfile
├── __init__.py
├── app.py
├── assets
│   ├── dropdown.css
│   └── favicon.ico
├── calculations.py
├── componentbuilder.py
├── database
├── elementstyling.py
├── find_inventories.py
├── gps.py
├── gpsvis.py
├── logs
├── monga.py
├── monph.py
├── monu.py
├── monvct.py
├── requirements.txt
├── seismic.py
├── station_inventories
│   ├── CONZ.xml
│   ├── ELHT.xml
│   ├── HOO.xml
│   └── NAUS.xml
└── weather.py
```

Within the "app" folder, there is:
- The Dockerfile: which specifies how to build our app within a Docker container
- assets: contain .css files used to style the dashboard
- station_inventories: a folder with XML files containing information about the 4 seismic stations from which data is collected
- ALL the other files within the directory correspond to a specific page within the web app:
    -  Ex: app.py contains the home-page of the site, gps.py contains the GPS Visualization page of the site, seismic.py contains the Seismic page of the website, monph.py contains the page containing pressure & humidity data of the instrument, etc.
    -  The names of the files directly correspond to the page they represent
    -  So, if you ever want to edit the layout of a particular page, go to the file corresponding to that page within the app directory!

Now let's look at the backend directory:
Here's another tree visualization -->
```bash
backend
├── Dockerfile
├── gps_data_pull.py
├── logmethods.py
├── main_download.py
├── requirements.txt
├── seismic_data_pull.py
└── weather_data_pull.py
```
The back-end directory of the project contains programs to facilitate automatic downloading of seismic, GPS, & weather data as they become available. Though currently, data is being downloaded using the public repositories mentioned above, the sources will eventually change to be from the SGIP. If you were wondering, the programs use the Python library APScheduler to schedule automated downloads of files. In this repository, as you might guess, gps_data_pull.py, seismic_data_pull.py, & weather_data_pull.py contain methods to download data from their corresponding repositories. main_download.py contains the program to organize when the downloads should happen. Finally, logmethods.py contains a method that is used to log what files are downloaded within the logs folder (located in the main directory of the project).

Finally, let's look at the database directory of the project:
```bash
database
├── create_db.py
└── sqlitedata.db
```
Within the database directory, there are 2 files. <code>createdb.py</code> is used to intialize an empty SQLite3 with the correct table specifications. You might notice, the other file (sqlitedata.db) is not present in the Github. sqlitedata.db stores the entire SQLite database; it is too large to be stored on Github, but it is available on Dropbox. When running the project, download sqlitedata.db from the dropbox and place it within the database directory.

## Database Schema
Let's quickly discuss the schema of the SQLite3 database. The database contains 4 tables (corresponding to each type of data):

Table #1: weather_data
<br>
<code>
CREATE TABLE weather_data (
            timestamp TEXT PRIMARY KEY NOT NULL,
            temperature REAL,
            pressure REAL, 
            relhumidity REAL   
            );
    </code>
   <br>
The weather_data table contains, as you might guess, weather data. It contains 4 columns: timestamp (representing the time of data collection), and the 3 data points of temperature, pressure, & relative humidity. The time of data collection is the primary key of this table.

Table #2: seismic_data
<br>
<code>
    CREATE TABLE seismic_data (
    timestamp TEXT,
    station TEXT,
    mseed BLOB,
    PRIMARY KEY (timestamp, station)  
    );
 </code>
 <br>

Before we discuss the schema of the seismic_table, let's first discuss how seismic data is stored. Seismic data are stored as ".mseed" files, which are the standard format for seismological data. To store these files within the data table, we convert the file to the BLOB type, so that it is compatible with SQLite. Within the seismic_data table, there are 3 columns: timestamp (the time of data collection), the station (a String corresponding to the name of the seismic station), and the mseed file (stored as a BLOB). The primary key of this table are the timestamp & the station together, as they uniquely identify each row.

Table #3: gps_data
<br>
<code>
CREATE TABLE IF NOT EXISTS "gps_data" (
    timestamp TEXT,
    station TEXT,
    eastingsi REAL, 
    eastingsf REAL, 
    northingsi REAL,
    northingsf REAL, 
    verticali REAL, 
    verticalf REAL,
    reflongitude REAL, 
    currlatitude REAL, 
    currlongitude REAL, 
    currheight REAL, 
    PRIMARY KEY (timestamp, station)
    );
</code>
<br>

The gps_data table, much like the seismic_table, also contains 2 columns corresponding to the time of data collection and station name. The rest of the columns contain a variety of information about the location of the station, including relative east/north/vertical location from a meridian, as well as the longitude, longitude, & height.

Table #4: sysmon_data
<br>
<code>
    CREATE TABLE sysmon_data (
    timestamp TEXT,
    station TEXT,
    voltageToBattery REAL, 
    currentToBattery REAL, 
    voltageFrBattery REAL, 
    currentFrBattery REAL, 
    tempInside REAL, 
    pressInside REAL, 
    humidInside REAL, 
    tempOutside REAL, 
    pressOutside REAL, 
    humidOutside REAL, 
    gyroX REAL, 
    gyroY REAL, 
    gyroZ REAL, 
    accelX REAL, 
    accelY REAL, 
    accelZ REAL, 
    cpu REAL, 
    memory REAL,
    diskspace REAL,              
    PRIMARY KEY (timestamp, station)
    );
 </code>
 <br>
 If you've been paying attention, you might notice I didn't really give much information about the system monitoring section of the dashboard. The purpose of the system monitoring page within the dashboard is to give utility information about the SGIP instrument when it is launched (including its temperature, its movement, & its internal hardware). However, as this data is not available, the web dashboard uses simulated data from a previous MIT Haystack mission. Some of its columns represent voltage to the battery of the instrument, the acceleration/gyroscope records, as well as how much memory/diskspace is available for data collection within the SGIP at various points in time. Like the other tables, the primary key of this table is the time of data collection as well as the station (in case there are multiple instruments being monitored using the dashboard).
 
 ## Customization
 
 Let's get to the fun part: how can you customize the SGIP Dashboard to fit your needs?
 
Let's first discuss adding/removing components. An important file to understand that will be immensely useful to add/remove graphs is the componentbuilder.py file located within the app directory. This file is used to create components within all pages of the website, so if you need some guidance, you can look at how it is used to create each page (ex. look at seismic.py).
 
 Within componentbuilder.py, there are 3 main methods: 
 - build_graph_component: used to create the standard graphs seen on the all visualization pages EXCEPT the home page (includes an expand button + description button)
 - build_form_component: used to create the graphs seen on the home page (which only have the expand button)
 - build_form_component: used to create the form inputs within each page (look at any page except the home page)

These methods are all really similar, & have descriptions in componentbuilder.py. Many of them take inputs of ids (which are used for the dash callbacks), as well as the actual text to be displayed within the component.

I believe the best way to understand is to look at an example:
Let's consider the spectrogram graph within the seismic page -->

Here is the code that creates the component:
<code>
spectrogram_graph = componentbuilder.build_graph_component("Spectrogram", "open-spec-button", "close-spec-button", "open-specq-button", "open-spec-modal-body", "open-spec-modal", "spectrogramgraph", "specq-modal", spectrogram_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    </code>

Consider each of the arguments:
- "Spectrogram": the title to be displayed on the graph component
- "open-spec-button": the id of the button to open the expand modal
- "close-spec-button": the id of the button to close the expand modal
- "open-specq-button": the id of the button to open the question modal
- "open-spec-modal-body": id of the expand-modal body 
- "open-spec-modal": id of the expand-modal
- "spectrogramgraph": id of the html.Div component the spectrogram graph will eventually go
- "specq-modal": id of the question-modal
- spectrogram_desc: description that will go within the question-modal
- elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP: css styling of the entire component



 
 ## Future Steps
Though RIS-Vis is currently capable of displaying visualizations are useful in evaluating the health of the Ross Ice Shelf, there are still many, many improvements to be made! Plenty of more analysis capabilities can be added: including using machine learning to detect concerning seismic events that could lead to shelf collapse, as well as 3-D visualizations of the movements of the ice shelves over time. It is our hope that RIS-Vis will one day be able to help scientists make conclusions about the health of the Ross Ice Shelf, and possibly create solutions to solve our planet's climate crisis.
 
 



