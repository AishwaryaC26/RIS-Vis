# RIS-Vis: MIT Haystack SGIP Data Monitor and Visualizer

Built by Aishwarya Chakravarthy (MIT Haystack REU 2023)

## Table of contents
- Introduction
- Requirements
- Technologies Used
- Installation
- Configuration
- Future Steps

## Introduction
RIS-Vis is a web dashboard application built with the purpose of helping visualize seismic, geodetic, weather, & system monitoring data from the Seismo-Geodetic Ice Penetrator (SGIP) built by the MIT Haystack Observatory. The SGIP is an instrument with seismic and geodetic sensors embedded that will collect data from the Ross Ice Shelf (in Antarctica) when deployed. Since there is currently no data from the SGIP available (as it has not been launched yet), the web application in this repository uses a variety of publicly available data from the IRIS DMC, the Nevada Geodetic Laboratory, & the University of Wisconsin-Madison Automatic Weather Station database. These sources respectively collect seismic, geodetic, and weather data from locations around Antarctica/the rest of the world, including the Ross Ice Shelf. Features of the dashboard include visualizing spectrograms, power spectral densities, GPS station plots, and many more!

## Requirements
To run RIS-Vis on your computer, it is necessary to have Docker installed. Please follow the instructions at https://docs.docker.com/get-docker/ to install Docker on your computer.

## Technologies Used
RIS-Vis was built using Python for the front-end and SQLite3 for the backend database. Specifically, the front-end was built using the Plotly Dash web framework, popularly used for creating interactive data visualizations. 

## Installation
To build RIS-Vis on your own computer:
- Go to your terminal & run <code> git clone https://github.mit.edu/barrettj/achakrav_reu2023.git </code> into your preferred location
- Then, within terminal, go to the directory with the repository
- Run <code> docker-compose up --build </code>
- The web application should run at http://localhost:8080/!

To stop running RIS-Vis:
-  Run the command "docker-compose down" on terminal in the project folder directory
-  To restart the project again, you can simply call "docker-compose up --build"

## Configuration
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
The back-end directory of the project contains programs to facilitate automatic downloading of seismic, GPS, & weather data as they become available. Though currently, data is being downloaded using the public repositories mentioned above, the sources will eventually change to be from the SGIP. If you were wondering, the programs use the Python library APScheduler to schedule automated downloads of files. In this repository, as you might guess, gps_data_pull.py, seismic_data_pull.py, & weather_data_pull.py contain methods to download data from their corresponding repositories. main_download.py contains the program to organize when the downloads should happen. Finally, logmethods.py contains a method that is used to log what files are downloaded within the logs folder (located in 
the main directory of the project).






