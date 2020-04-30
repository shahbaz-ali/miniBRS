#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

"""
This is module has helper function for date time
"""

import calendar
from datetime import timedelta, datetime
from airflow.utils.log.logging_mixin import LoggingMixin
from plugins.mbrs.utils.exceptions import BadStartDatePreset
from airflow.utils.dates import cron_presets
from airflow.utils.timezone import utcnow

cron_presets['@half-hourly'] = '*/30 * * * *'


def get_start_date(start_date):
    """
    Wrapper over the function days_ago, used to check the valid start_date config format
    :param start_date:
    :return: datetime
    :exception BadStartDatePreset
    """
    if str(start_date).__contains__('days'):
        preset = str(start_date)[-4:]
        value = str(start_date)[:-4]
    elif str(start_date).__contains__('day'):
        preset = str(start_date)[-3:]
        value = str(start_date)[:-3]
    else:
        raise BadStartDatePreset

    value = int(value)

    if value < 0:
        value = -value
        LoggingMixin().log.warning("Start date cannot be negative integer")

    if preset == 'mo':
        return days_ago(months_ago(int(value)))
    elif preset == 'day' or preset == 'days':
        return days_ago(int(value))
    else:
        raise BadStartDatePreset


def days_ago(n, hour=0, minute=0, second=0, microsecond=0):
    """
    Get a datetime object representing `n` days ago. By default the time is
    set to midnight.
    """
    if isinstance(n, str):
        raise TypeError("Number of days cannot be of type str")

    today = utcnow().replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond)
    return (today - timedelta(days=n)).replace(tzinfo=None)


def months_ago(n, hour=0, minute=0, second=0, microsecond=0):
    """
        returns number of days  representing `n` months ago. By default the time is
        set to midnight.
        :return int
        """

    days = 0
    today = datetime.now().replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond
    )

    i = n-1

    while i > 0:
        if calendar.isleap(today.year) and i == 2:
            days += calendar.mdays[i] + 1
        else:
            days += calendar.mdays[i]

        i -= 1

    days += today.day

    return days - 1


def one_month_ago(execution_date: str):
    """
    Get number of days in one month
    :param execution_date:
    :return: int
    """
    date = datetime.strptime(execution_date[:19], "%Y-%m-%dT%H:%M:%S")
    days = 0
    if date.month == 1:
        days = calendar.mdays[12]
    else:
        if date.month == 3 and calendar.isleap(date.year):
            days = calendar.mdays[date.month - 1] + 1
        else:
            days = calendar.mdays[date.month - 1]

    return days
