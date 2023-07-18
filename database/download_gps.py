## this will also be executed every night at 3 AM 

import requests
import sys
import os
from dotenv import load_dotenv
import ast
import sqlite3
from sqlite3 import Error
from datetime import date, datetime, timedelta

''' GPS Data is Formatted 
            1.   COVE      station name
            2.   10JUL28   date
            3.   2010.5708 decimal year
            4.   55405     modified Julian day
            5.   1594      GPS week
            6.   3         day of GPS week
            7.  -112.8     longitude (degrees) of reference meridian
            8.  -3815      eastings (m), integer portion (from ref. meridian)
            9.  -0.638876  eastings (m), fractional portion
            10.  4276712   northings (m), integer portion (from equator)
            11.  0.811250  northings (m), fractional portion
            12.  1687      vertical (m), integer portion
            13.  0.349158  vertical (m), fractional portion
            14.  0.1800    antenna height (m) assumed from Rinex header
            15.  0.000902  east sigma (m)
            16.  0.000992  north sigma (m)
            17.  0.004512  vertical sigma (m)
            18.  0.091352  east-north correlation coefficient
            19. -0.536983  east-vertical correlation coefficient
            20.  0.041338  north-vertical correlation coefficient
            21.   38.6235432767 nominal station latitude
            22. -112.8438158344 nominal station longitude
            23. 1687.34916      nominal station height
            '''

load_dotenv()

## gps stations
gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])
print(gps_stations)

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn

def download_gps_data(url, conn, station_name):
    #station: FTP4
    # Makes request of URL, stores response in variable r
    db_name = "gps_data"
    r = requests.get(url)
    cur = conn.cursor()
    all_data = r.text
    all_lines = all_data.split("\n") ## getting all lines from response

    ind = len(all_lines) - 1 ## start from last row of table

    while ind > 0:
        if all_lines[ind]:
            curr_line = all_lines[ind].split() ## gets current line
            datetime_str = curr_line[1]
            datetime_obj = datetime.strptime(datetime_str, "%y%b%d")

            check_query = f"""SELECT EXISTS(SELECT * FROM {db_name} WHERE timestamp=? AND station=?);"""
            check_data_tuple = (str(datetime_obj),station_name,)
            cur.execute(check_query, check_data_tuple)
            check_res = cur.fetchall()

            if check_res[0][0] == 1:
                break
            ### now you are planning to add it to database
            ##Data was found- so add file to logs
            lines = None
            with open("logs/gps_log.txt", "r+") as f:
                lines = f.readlines()
                lines = [j.strip() for j in lines if j and j!="\n"]
                if not lines:
                    f.write("Station Date Data-date")
                if len(lines) <= 500:
                    lines = None
                elif len(lines) > 500:
                    lines = lines[len(lines) - 150:]
                f.close()
            if lines:
                with open("logs/gps_log.txt", "w") as sf:
                    sf.write("Station Date Data-date")
                    for l in lines:
                        sf.write("\n"+l)
                    sf.close()
            with open("logs/gps_log.txt", "a") as f:
                f.write(f"""\n{station_name} {str(date.today()).replace('-', '/')} {str(datetime_obj)[:10].replace('-', '/')}""")
                f.close()

            query = f"""
            INSERT INTO {db_name} (timestamp, station, eastingsi, eastingsf, northingsi, northingsf, 
            verticali, verticalf, reflongitude)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);"""
            
            data_tuple = (str(datetime_obj), station_name, curr_line[7], curr_line[8], curr_line[9], 
                          curr_line[10], curr_line[11], curr_line[12], curr_line[6])
            cur.execute(query, data_tuple) ## inserted

        ind -= 1


def download_nightly_gps_data():
    conn = create_connection("database/sqlitedata.db")
    for station in gps_stations: 
        download_gps_data(f"""http://geodesy.unr.edu/gps_timeseries/tenv3/IGS14/{station}.tenv3""", conn, station)
    conn.commit()
    conn.close()
