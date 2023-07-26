import wget
import os
from dotenv import load_dotenv
import pandas as pd
import sqlite3
from sqlite3 import Error
import datetime as datetime
import urllib
from datetime import date
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

def download_weather_data(conn):
    cur = conn.cursor()
    start_year = 2002
    start = datetime.datetime(2002, 1, 1, 0, 0, 0)
    k = 0
    for i in range(268):
        k = (k + 1) % 13
        if k == 0: k = 1
        if k <10:
            link = f"""{base_link}/{start.year}/{station}{start.year}0{k}q3h.txt"""
        else: 
            link = f"""{base_link}/{start.year}/{station}{start.year}{k}q3h.txt"""
        with open("logs/weather_log.txt", "r+") as f:
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
            with open("logs/weather_log.txt", "w") as sf:
                sf.write("Date Filename")
                for l in lines:
                    sf.write("\n"+l)
                sf.close()
        with open("logs/weather_log.txt", "a") as f:
            f.write(f"""\n{date.today()} {link}""")
            f.close()
        try:
            wget.download(link, out = "database/weatherdata.csv")
            with open("database/weatherdata.csv") as downloaded_file:
                linenum = 1
                for line in downloaded_file:
                    if linenum <= 2:
                        linenum += 1
                    else:
                        arr = line.split()
                        db_name = "weather_data"
                        query = f"""
                        INSERT INTO {db_name} (timestamp, temperature, 
                        pressure, relhumidity)
                        VALUES(?, ?, ?, ?);"""
                        data_tuple = (str(start), arr[5], arr[6], arr[9])
                        start += datetime.timedelta(hours = 3)
            os.remove("database/weatherdata.csv")
        
        except urllib.error.HTTPError as e:
            print("failed")

        
                
conn = create_connection("database/sqlitedata.db")
download_weather_data(conn)
conn.commit()
conn.close()