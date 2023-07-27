from apscheduler.schedulers.blocking import BlockingScheduler
from seismic_data_pull import nightly_download_mseed_waveform
from gps_data_pull import download_nightly_gps_data
from weather_data_pull import monthly_download_weather_data

def get_seismic_data():
    nightly_download_mseed_waveform()    

def get_gps_data():
    download_nightly_gps_data()

def get_weather_data():
    monthly_download_weather_data()

## uses APScheduler to create list of tasks that will be executed at certain times
'''
Currently, 
- seismic data is downloaded every night at 3 AM 
- GPS data is downloaded every night at 4 AM
- Weather data will be downloaded on the first day of every month at 10 AM
'''
if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone="America/New_York", misfire_grace_time = None, coalesce = True)
    scheduler.add_job(get_seismic_data, 'cron', minute='00', hour='3', day='*', year='*', month='*')
    scheduler.add_job(get_gps_data, 'cron', minute='00', hour='4', day='*', year='*', month='*')
    scheduler.add_job(get_weather_data, 'cron', minute='0', hour='10', day='1', year='*', month='*')
    scheduler.start()