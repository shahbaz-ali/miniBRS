#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali


from airflow.utils.dates import cron_presets

cron_presets['@half-hourly'] ='*/30 * * * *'
