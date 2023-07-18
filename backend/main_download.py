import os
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from seismic_data_pull import nightly_download_mseed_waveform
from gps_data_pull import download_nightly_gps_data
from weather_data_pull import monthly_download_weather_data
import sqlite3


def get_seismic_data():
    nightly_download_mseed_waveform()    

def get_gps_data():
    download_nightly_gps_data()

def get_weather_data():
    monthly_download_weather_data()

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone="America/New_York", misfire_grace_time = None, coalesce = True)
    scheduler.add_job(get_seismic_data, 'cron', minute='43', hour='10', day='*', year='*', month='*')
    scheduler.add_job(get_gps_data, 'cron', minute='45', hour='9', day='*', year='*', month='*')
    scheduler.add_job(get_weather_data, 'cron', minute='0', hour='10', day='1', year='*', month='*')
    scheduler.start()