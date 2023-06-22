import os
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from obspy.clients.fdsn import Client
from IRIS_seismic_data.helpers.seismic_data_pull import 

def get_data(cl):
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename="./logs/main.log", format='%(asctime)s:%(levelname)s:%(message)s')
    scheduler = BlockingScheduler()
    scheduler.add_job(get_data(), 'cron', minute='00', hour='03', day='*', year='*', month='*')
    scheduler.start()