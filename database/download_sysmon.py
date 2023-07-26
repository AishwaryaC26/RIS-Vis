
import sqlite3
from sqlite3 import Error
from datetime import datetime


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

def downlaod_sysmon_data(filename, conn):
    db_name = "sysmon_data"
    query = f"""
            INSERT INTO {db_name} (timestamp, station, voltageToBattery, currentToBattery, voltageFrBattery, 
            currentFrBattery, tempInside, pressInside, humidInside, tempOutside, pressOutside, humidOutside, 
            gyroX, gyroY, gyroZ, accelX, accelY, accelZ, cpu, memory, diskspace)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    check_query = f"""SELECT timestamp ,station FROM {db_name} WHERE timestamp=? AND station=?"""
    cur = conn.cursor()
    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break
            arr = line.strip().split(",")
            date = datetime.strptime(arr[1], "%Y-%j-%H%M%S")
            print(arr[1])
            print(date)
            print(arr[0])
            cur.execute(check_query, (str(date), arr[0]))
            result = cur.fetchone()
            if not result:
                data_tuple = (str(date), arr[0], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7], 
                            arr[8], arr[9], arr[10], arr[11], arr[12], arr[13], arr[14], arr[15],
                            arr[16], arr[17], arr[18], arr[19], arr[20])
                cur.execute(query, data_tuple)
            


def download_nightly_sysmon_data():
    conn = create_connection("database/sqlitedata.db")
    downlaod_sysmon_data(f"""database/smm_logs2.txt""", conn)
    conn.commit()
    conn.close()

download_nightly_sysmon_data()