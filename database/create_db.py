'''
Program to create SQLite Datbase:
This program should only be run once when the app is initially being deployed.
If an SQLite Database has already been created, it is not necessary to run 
this program.
'''

import sqlite3
from sqlite3 import Error

import os
from dotenv import load_dotenv
import ast

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

def create_table(conn, create_table_sql):
    '''
    Create an SQL table using the create_table_sql string
    '''
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


conn = create_connection("database/sqlitedata.db")

if __name__ == '__main__':
    load_dotenv()
    stations = list(ast.literal_eval(os.environ["SEISMIC_STATIONS"]).keys())

    create_table(conn, """ CREATE TABLE IF NOT EXISTS seismic_data (
    timestamp TEXT,
    station TEXT,
    mseed BLOB,
    PRIMARY KEY (timestamp, station)  
    ); """)

    create_table(conn, """ CREATE TABLE IF NOT EXISTS weather_data (
    timestamp TEXT PRIMARY KEY NOT NULL,
    temperature REAL,
    pressure REAL, 
    relhumidity REAL   
    ); """)

    create_table(conn, """CREATE TABLE IF NOT EXISTS gps_data (
    timestamp TEXT,
    station TEXT,
    east REAL, 
    north REAL, 
    up REAL, 
    PRIMARY KEY (timestamp, station)
    ); """)

    create_table(conn, """CREATE TABLE IF NOT EXISTS gps_data2 (
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
    ); """)



    



    '''
    for stat in stations:
    create_table(conn, """ CREATE TABLE IF NOT EXISTS seismic_""" +stat+""" (
    timestamp TEXT PRIMARY KEY NOT NULL,
    mseed BLOB  
    ); """)

    create_table(conn, """ CREATE TABLE IF NOT EXISTS weather_data (
    timestamp TEXT PRIMARY KEY NOT NULL,
    temperature REAL,
    pressure REAL, 
    relhumidity REAL   
    ); """)

    create_table(conn, """CREATE TABLE IF NOT EXISTS GPS_FTP4 (
    timestamp TEXT PRIMARY KEY NOT NULL,
    east REAL, 
    north REAL, 
    up REAL
    ); """)'''
    
    conn.commit()
    conn.close()


                          
        


