'''
For weather data:
The database will be checked every month, and all new files will be downloaded
'''
import wget
import os
from dotenv import load_dotenv
import pandas as pd
import sqlite3
from sqlite3 import Error
from datetime import datetime, date, timedelta
import urllib
import requests
from dateutil.relativedelta import relativedelta
load_dotenv()

station = os.environ["WEATHER_STATION"]
base_link = "https://amrc.ssec.wisc.edu/data/ftp/pub/aws/q3h"

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

def create_weather_link(year, station, month):
    if month < 10:
        return f"""{base_link}/{year}/{station}{year}0{month}q3h.txt"""
    else:
        return f"""{base_link}/{year}/{station}{year}{month}q3h.txt"""

def write_to_logfile(filename, link):
    lines = None
    with open(filename, "r+") as f:
        lines = f.readlines()
        lines = [j.strip() for j in lines if j and j!="\n"]
        if not lines:
            f.write("Date Filename")
        if len(lines) <= 500:
            lines = None
        elif len(lines) > 500:
            lines = lines[len(lines) - 150:]
        f.close()
    if lines:
        with open(filename, "w") as sf:
            sf.write("Date Filename")
            for l in lines:
                sf.write("\n"+l)
            sf.close()
    with open(filename, "a") as f:
        f.write(f"""\n{str(date.today()).replace('-', '/')} {link}""")
        f.close()

def download_weather_data(conn):
    ## find the last data available in the database rn
    cur = conn.cursor()
    db_name = "weather_data"
    empty_db = False

    ##today's date
    today = date.today()
    curr_check = datetime(today.year, today.month, 1, 0, 0, 0)

    init_query = f"""SELECT timestamp FROM {db_name} ORDER BY timestamp DESC LIMIT 1;"""
    cur.execute(init_query)
    init_res = cur.fetchall() ## list will contain last data available
    print(init_res)
    if not init_res:
        empty_db = True
        init_time = curr_check
    else:
        init_time = datetime.strptime(init_res[0][0], '%Y-%m-%d %H:%M:%S')
        init_time = datetime(init_time.year, init_time.month, 1, 0, 0, 0)
    
    while init_time <= curr_check and empty_db:
        print(init_time)
        link = create_weather_link(init_time.year, station, init_time.month)
        curr_response = requests.get(link)
        init_time_cp = init_time

        if curr_response.status_code != 200:
            print("New data not available. Checking next month.")
            continue
        else:
            ##log that you downloaded it
            write_to_logfile("logs/weather_log.txt", link)
            
            all_data = curr_response.text
            all_lines = all_data.split("\n") ## getting all lines from response
            for i in range(2, len(all_lines)):
                line = all_lines[i]
                if line:
                    arr = line.split()
                    query = f"""
                                INSERT INTO {db_name} (timestamp, temperature, 
                                pressure, relhumidity)
                                VALUES(?, ?, ?, ?);"""
                    data_tuple = (str(init_time_cp), arr[5], arr[6], arr[9])
                    cur.execute(query, data_tuple)
                    init_time_cp += datetime.timedelta(hours = 3)
        init_time += relativedelta(months = 1)
        

def monthly_download_weather_data():
    conn = create_connection("database/sqlitedata.db")
    download_weather_data(conn)
    conn.commit()
    conn.close()

