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

def fetch_servicenow_record_count(table_name,execution_date,**kwargs):
    """
    This method calls the servicenow api for a particular table and timeperiod
    and gets count of records for a particular table
    :param table_name for which count of records is to be checked:
    :return: task_id
    """

    try:

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

            execution_datetime = datetime.strptime(execution_date[:19], "%Y-%m-%dT%H:%M:%S")

            to_time = datetime(
                year=execution_datetime.year,
                month=execution_datetime.month,
                day=execution_datetime.day,
                hour=execution_datetime.hour,
                minute=execution_datetime.minute,
                second=execution_datetime.second,
                tzinfo=pendulum.timezone("UTC")
            )
            from_time = to_time + freq_param

        except KeyError as e:
            raise ConfigVariableNotFoundException()
        try:
            credentials_snow = BaseHook.get_connection("servicenow_default")
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
        elif (frequency == 'daily'):
            freq_param = timedelta(days=-1)

        elif (frequency == 'half-hourly'):
            freq_param = timedelta(minutes=-30)
        else:
            return 'count_within_threshold'


    except Exception as e:

        kwargs['ti'].xcom_push(
            key='exception',
            value=str(e)
        )

        raise


def on_failure_email(dag_id,task_id,message):
    '''
    This function is used to send an email to the registered email id
    in the configuration variable 'config'
    :param dag_id: str, name of the dag
    :param task_id: str, name of the task which failed
    :param message: str, exception trace that lead to the failure
    :return: None
    '''

    message = '<img src="https://airflow.apache.org/images/feature-image.png" width="400" height="100"/>' \
              '<h2>AIRFLOW TASK FAILURE:</h2><hr/>' \
              '<strong>DAG : </strong>    {} <br/><hr/>' \
              '<strong>TASKS:</strong>  {}<br/><hr/>' \
              '<strong>Reason:</strong> {}<br/><hr/>' \
        .format(dag_id,task_id,message)

    try:
        config = json.loads(Variable.get("config"))
        email = config['email']
    except NameError as e:
        raise ConfigVariableNotFoundException()

    send_email(
        to=email,
        subject='Airflow Notification',
        html_content=message
    )

def on_failure_context(dag_id,task_id,execution_date,msg,run_id):

    '''
    This function is used to save the error information as a variable in the
    variable's table of the airflow meta database.

    :param dag_id: str, name of the dag_id
    :param task_id: str, name of the failing task
    :param execution_date: str, dag time execution
    :param msg: str, exception name that lead to the failure
    :return: None
    '''

    execution_date = execution_date.replace('T', ' ')[0:19]
    key = '{}${}'.format(execution_date, dag_id)

    value = {
        'dag_id' : dag_id,
        'execution_date' : execution_date,
        'task_id' : task_id,
        'run_id' : run_id,
        'error_msg' : msg
    }

    Variable.set(
        key=key,
        value=json.dumps(value),
        session=Session
    )


def on_failure(context):

    '''
    This is a callback function used by the Task's to notify failure events
    :param context: context of the task execution object
    :return:
    '''

    instance = context['task_instance']
    dag_id = str(instance.dag_id)
    task_id = str(instance.task_id)
    msg = str(context['exception'])
    execution_date = str(instance.execution_date)
    run_id = str(context['run_id'])

    on_failure_context(
        dag_id = dag_id,
        task_id= task_id,
        execution_date= execution_date,
        msg= msg,
        run_id=run_id
    )

    on_failure_email(
        dag_id=dag_id,
        task_id=task_id,
        message=msg
    )

def clean_up(variable_key):
    try:
        variable_split = variable_key.split("$")
        exec_date = variable_split[0]
        table_name = variable_split[1]
        Variable.delete(variable_key)

        r_config = json.loads(Variable.get("r_config"))
        if table_name in r_config:
            exec_dates = r_config[table_name]
            if exec_date in exec_dates:
                exec_dates.remove(exec_date)
                r_config[table_name] = exec_dates

            if len(r_config[table_name]) == 0:
                del r_config[table_name]
        if len(r_config) != 0:
            Variable.set(
                key="r_config",
                value=json.dumps(r_config)
            )
        else:
            Variable.delete('r_config')
    except Exception as e:
        print(e)