#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from datetime import timedelta, datetime
from plugins.mbrs.utils.exceptions import BadStartDatePreset
from airflow.utils.dates import cron_presets

cron_presets['@half-hourly'] ='*/30 * * * *'


def get_start_date(start_date):

    preset = str(start_date)[-2:]
    value = str(start_date)[:-2]
    present = datetime.now()
    s_date = present + timedelta(days=-1)
    if preset == 'mo':
        s_date = present + timedelta(weeks= -4*int(value))
    elif preset == 'wk':
        s_date = present +timedelta(weeks=int(value))
    elif preset == 'da':
        s_date = present + timedelta(days=-1 * int(value))
    else:
        raise BadStartDatePreset


    return datetime(
        s_date.year,
        s_date.month,
        s_date.day,
        s_date.hour,
        s_date.minute,
        0
    )