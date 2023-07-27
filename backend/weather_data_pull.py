'''
For weather data:
The database will be checked every month, and all new files available will be downloaded
'''
import os
from dotenv import load_dotenv
import sqlite3
from sqlite3 import Error
from datetime import datetime, date, timedelta
import requests
from dateutil.relativedelta import relativedelta
import logmethods
load_dotenv()

station = os.environ["WEATHER_STATION"]
base_link = os.environ["WEATHER_BASE_LINK"]
database_name = os.environ["DATABASE_NAME"]
weather_table = os.environ["WEATHER_TABLE_NAME"]
weather_log = os.environ["WEATHER_LOG_LOC"]


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

def download_weather_data(conn):
    ## find the last data available in the database rn
    cur = conn.cursor()
    table_name = weather_table

    ##today's date
    today = date.today()
    curr_check = datetime(today.year, today.month, 1, 0, 0, 0)

    init_query = f"""SELECT timestamp FROM {table_name} ORDER BY timestamp DESC LIMIT 1;"""
    cur.execute(init_query)
    init_res = cur.fetchall() ## list will contain last data available
    if not init_res:
        init_time = curr_check
    else:
        init_time = datetime.strptime(init_res[0][0], '%Y-%m-%d %H:%M:%S')
        init_time = datetime(init_time.year, init_time.month, 1, 0, 0, 0) + relativedelta(months = 1) ## find the last month available and then add 1 month
    
    while init_time <= curr_check:
        link = create_weather_link(init_time.year, station, init_time.month)
        curr_response = requests.get(link)
        init_time_cp = init_time

        if curr_response.status_code != 200:
            print("New data not available.")
            init_time += relativedelta(months = 1)
            continue
        else:
            ##log that you downloaded it
            new_line = f"""\n{str(date.today()).replace('-', '/')} {link}"""
            logmethods.write_to_log(weather_log, "Download-Date Filename", str(new_line))
            
            all_data = curr_response.text
            all_lines = all_data.split("\n") ## getting all lines from response
            for i in range(2, len(all_lines)):
                line = all_lines[i]
                if line:
                    arr = line.split()
                    query = f"""
                                INSERT INTO {table_name} (timestamp, temperature, 
                                pressure, relhumidity)
                                VALUES(?, ?, ?, ?);"""
                    data_tuple = (str(init_time_cp), arr[5], arr[6], arr[9])
                    cur.execute(query, data_tuple)
                    init_time_cp += timedelta(hours = 3)
        init_time += relativedelta(months = 1)
        

def monthly_download_weather_data():
    conn = create_connection(database_name)
    download_weather_data(conn)
    conn.commit()
    conn.close()
