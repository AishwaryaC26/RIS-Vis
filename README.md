# RIS-Vis: MIT Haystack SGIP Data Monitor and Visualizer

Built by Aishwarya Chakravarthy

## Table of contents
- Introduction
- Technologies Used
- Installation
- Configuration
- Future Steps

## Introduction
RIS-Vis is a web dashboard application built with the purpose of helping visualize seismic, geodetic, weather, & system monitoring data from the Seismo-Geodetic Ice Penetrator (SGIP) built by the MIT Haystack Observatory. The SGIP is an instrument with seismic and geodetic sensors embedded that will collect data from the Ross Ice Shelf (in Antarctica) when deployed. Since there is currently no data from the SGIP available (as it has not been launched yet), the web application in this repository uses a variety of publicly available data from the IRIS DMC, the Nevada Geodetic Laboratory, & the University of Wisconsin-Madison Automatic Weather Station database. These sources respectively collect seismic, geodetic, and weather data from locations around Antarctica/the rest of the world, including the Ross Ice Shelf. Features of the dashboard include visualizing spectrograms, power spectral densities, GPS station plots, and many more!

## Technologies Used
RIS-Vis was built using Python for the front-end and SQLite3 for the backend database. Specifically, the front-end was built using the Plotly Dash web framework, popularly used for creating interactive data visualizations. 

## Installation
To build RIS-Vis on your own computer:
- Go to your terminal & run "git clone https://github.mit.edu/barrettj/achakrav_reu2023.git" into your preferred location
- Then, within terminal, go to the directory with the repository
- Run "docker-compose up --build"
- The web application should run at "http://localhost:8080/"!

To stop running RIS-Vis:
-  Run the command "docker-compose down" on terminal in the project folder directory
-  To restart the project again, you can simply call "docker-compose up --build"

## Configuration
RIS-Vis was built with an emphasis on making it simple to add/remove components!

Before we discuss how to add/remove components, let's take a tour of the repository:

Here is a 






