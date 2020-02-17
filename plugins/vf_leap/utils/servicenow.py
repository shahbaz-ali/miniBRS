#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali
from plugins.vf_leap.utils.servicenow_client import ServiceNowHibernateException, ServiceNowAPIException
from plugins.vf_leap.hooks.servicenow_hook import ServiceNowHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.hooks.base_hook import BaseHook
from airflow.hooks.sqlite_hook import SqliteHook
from airflow.models import Variable
from airflow.exceptions import AirflowException
import json, os, requests, pytz
from datetime import datetime,timedelta

def fetch_servicenow_record_count(table_name):
    """
    This method calls the servicenow api for a particular table and timeperiod
    and gets count of records for a particular table
    :param table_name for which count of records is to be checked:
    :return: task_id
    """


    try:
        # Load Configuration Data
        config = json.loads(Variable.get("config"))
        frequency = config['frequency']

        if (frequency == 'hourly'):
            freq_param = timedelta(hours = -1)

        elif (frequency == 'daily'):
            freq_param = timedelta(days=-1)
        else:
            freq_param = timedelta(hours =-1)

        time_now = datetime.now()
        timezone = pytz.timezone("Etc/UTC")
        to_time = timezone.localize(time_now)
        from_time = to_time + freq_param

    except KeyError as e:
        LoggingMixin().log.error("No configuration found !")

    try:
        credentials_snow = BaseHook.get_connection("snow_id")
        login = credentials_snow.login
        password = credentials_snow.password
        host = credentials_snow.host
    except AirflowException as e:
        LoggingMixin().log.error("No Connection Found for ServiceNow Instance !")


    try:
        service_now_hook = ServiceNowHook(
            host=host,
            login=login,
            password=password
        )
        response = service_now_hook.api_call(
            route='/api/now/stats/{}'.format(table_name),
            accept='application/json',
            query_params={
                'sysparm_count': 'true',
                'sysparm_query': "sys_updated_onBETWEENjavascript:gs.dateGenerate('{}','{}')@javascript:gs.dateGenerate('{}','{}')".format(
                    str(from_time.date()),
                    str(from_time.time()),
                    str(to_time.date()),
                    str(to_time.time())
                )
            }
        )
        print('response :' + response)
        count_of_records = int(json.loads(response)['result']['stats']['count'])

        log = LoggingMixin().log
        log.info("totals number of records %s ", str(count_of_records))

        if int(count_of_records) == 0:
            return 'count_is_zero'
        elif int(count_of_records) > config['threshold']:
            return 'count_exceeds_threshold'
        else:
            return 'count_within_threshold'


    except (ServiceNowHibernateException) as e:
        count_of_records = 0
        LoggingMixin().log.warning("%s service now instance is hibernated !", str(host))
        return None

    except ServiceNowAPIException as e:
        count_of_records = 0
        LoggingMixin().log.warning("%s service now api error !", str(host))
        return None

    except Exception as e:
        count_of_records = 0
        LoggingMixin().log.error("%s service now error ! ", str(host))
        LoggingMixin().log.error("%s", str(e))
        return None

