#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from plugins.vf_leap.hooks.servicenow_hook import ServiceNowHook
from plugins.vf_leap.utils.exceptions import ServiceNowConnectionNotFoundException, SFTPConnectionNotFoundException,ConfigVariableNotFoundException
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.settings import Session
from airflow.hooks.base_hook import BaseHook
from airflow.utils.email import send_email
from airflow.models import Variable
from airflow.exceptions import AirflowException
import json,pendulum
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

        to_time = datetime.now(tz=pendulum.timezone("UTC"))
        from_time = to_time + freq_param

    except KeyError as e:
        raise ConfigVariableNotFoundException()
    try:
        credentials_snow = BaseHook.get_connection("snow_id")
        login = credentials_snow.login
        password = credentials_snow.password
        host = credentials_snow.host
    except AirflowException as e:
        raise ServiceNowConnectionNotFoundException()


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


def on_failure(context):
    """
        The function that will be executed on failure.

        -> Send email
        -> Save error details as variable

        :param context: The context of the executed task.
        :type context: dict
        """
    message = '<img src="https://airflow.apache.org/images/feature-image.png" width="400" height="100"/>' \
              '<h2>AIRFLOW TASK FAILURE:</h2><hr/>'\
              '<strong>DAG : </strong>    {} <br/><hr/>' \
              '<strong>TASKS:</strong>  {}<br/><hr/>' \
              '<strong>Reason:</strong> {}<br/><hr/>' \
        .format(context['task_instance'].dag_id,
                context['task_instance'].task_id,
                context['exception'])

    try:
        config = json.loads(Variable.get("config"))
        email = config['email']
    except NameError as e:
        raise ConfigVariableNotFoundException()

    send_email(
        to=email,
        subject='Airflow',
        html_content=message
    )


    # Adds variable for error info

    Variable.set(
        key='{}${}'.format(context['task_instance'].execution_date,context['task_instance'].dag_id),
        value=str(context),
        session=Session
    )