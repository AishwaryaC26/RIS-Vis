import os
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from IRIS_seismic_data.helpers.seismic_data_pull import nightly_download_mseed_waveform



def get_data():
    nightly_download_mseed_waveform()


if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO, filename="./logs/main.log", format='%(asctime)s:%(levelname)s:%(message)s')
    scheduler = BlockingScheduler()
    scheduler.add_job(get_data, 'cron', minute='00', hour='03', day='*', year='*', month='*')
    scheduler.start()