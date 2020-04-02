#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from plugins.mbrs.hooks.servicenow_hook import ServiceNowHook
from plugins.mbrs.utils.exceptions import ServiceNowConnectionNotFoundException, ConfigVariableNotFoundException
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.db import provide_session
from plugins.mbrs.modals.recovery_modals import FailedDagRun
from plugins.mbrs.utils.dates import one_month_ago
from airflow.hooks.base_hook import BaseHook
from airflow.utils.email import send_email
from airflow.models import Variable
from airflow.exceptions import AirflowException
import json,pendulum
from datetime import datetime,timedelta
from plugins.mbrs.utils.exceptions import InvalidArguments


def fetch_servicenow_record_count(table_name, execution_date, **kwargs):
    """
    This method calls the service now api for a particular table and time period
    and gets count of records for a particular table
    :param: table_name : for which count of records is fetched
    :param: execution_date : airflow execution date of the dag
    :return: task_id
    """

    try:

        try:
            # Load Configuration Data
            config = json.loads(Variable.get("config"))
            frequency = config['frequency']
            execution_datetime = datetime.strptime(execution_date[:19], "%Y-%m-%dT%H:%M:%S")

            if frequency == 'hourly':
                freq_param = timedelta(hours = -1)

            elif frequency == 'daily':
                freq_param = timedelta(days=-1)
            elif frequency == 'monthly':
                freq_param = timedelta(days=-1*one_month_ago(execution_date))

            elif frequency == 'half-hourly':
                freq_param = timedelta(minutes=-30)
            else:
                freq_param = timedelta(hours=-1)

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
                'sysparm_query': "sys_updated_onBETWEENjavascript:gs.dateGenerate('{}','{}')"
                                 "@javascript:gs.dateGenerate('{}','{}')".format(str(from_time.date()),
                                                                                 str(from_time.time()),
                                                                                 str(to_time.date()),
                                                                                 str(to_time.time())
                                                                                 )
            }
        )
        print('response :' + response)
        count_of_records = int(json.loads(response)['result']['stats']['count'])

        log = LoggingMixin().log
        log.info("Getting count from: {}  to : {} ".format(from_time, to_time))
        log.info("totals number of records %s ", str(count_of_records))

        if int(count_of_records) == 0:
            return 'count_is_zero'
        elif int(count_of_records) > config['threshold']:
            return 'count_exceeds_threshold'
        else:
            return 'count_within_threshold'

    except Exception as e:

        kwargs['ti'].xcom_push(
            key='exception',
            value=str(e)
        )

        instance = kwargs['task_instance']
        dag_id = str(instance.dag_id)
        task_id = str(instance.task_id)
        msg = str(e)
        execution_date = str(instance.execution_date)
        run_id = str(kwargs['run_id'])

        execution_date = execution_date.replace('T', ' ')[0:19]
        key = '{}${}'.format(execution_date, dag_id)

        value = {
            'dag_id': dag_id,
            'execution_date': execution_date,
            'task_id': task_id,
            'run_id': run_id,
            'error_msg': msg
        }

        Variable.set(
            key=key,
            value=json.dumps(value)
        )

        raise


def on_failure_email(dag_id, task_id, message):
    """
    This function is used to send an email to the registered email id
    in the configuration variable 'config'
    :param dag_id: str, name of the dag
    :param task_id: str, name of the task which failed
    :param message: str, exception trace that lead to the failure
    :return: None
    """

    message = '<img src="https://airflow.apache.org/images/feature-image.png" width="400" height="100"/>' \
              '<h2>AIRFLOW TASK FAILURE:</h2><hr/>' \
              '<strong>DAG : </strong>    {} <br/><hr/>' \
              '<strong>TASKS:</strong>  {}<br/><hr/>' \
              '<strong>Reason:</strong> {}<br/><hr/>' \
        .format(dag_id, task_id, message)

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


def on_failure_context(dag_id, task_id, execution_date, msg, run_id):

    """
    This function is used to save the error information as a variable in the
    variable's table of the airflow meta database.

    :param dag_id: str, name of the dag_id
    :param task_id: str, name of the failing task
    :param execution_date: str, dag time execution
    :param msg: str, exception name that lead to the failure
    :param run_id: str, dag run_id
    :return: None
    """
    execution_date = execution_date.replace('T', ' ')[0:19]
    key = '{}${}'.format(execution_date, dag_id)

    value = {
        'dag_id': dag_id,
        'execution_date': execution_date,
        'task_id': task_id,
        'run_id': run_id,
        'error_msg': msg
    }

    Variable.set(
        key=key,
        value=json.dumps(value)
    )


def on_failure(**kwargs):

    """
    This is a callback function used by the Task's to notify failure events
    :return: None
    """

    instance = kwargs['task_instance']
    dag_id = str(instance.dag_id)
    task_id = str(instance.task_id)
    msg = str(kwargs['e'])
    execution_date = str(instance.execution_date)
    run_id = str(kwargs['run_id'])

    on_failure_context(
        dag_id=dag_id,
        task_id=task_id,
        execution_date=execution_date,
        msg=msg,
        run_id=run_id
    )

    # on_failure_email(
    #     dag_id=dag_id,
    #     task_id=task_id,
    #     message=msg
    # )


@provide_session
def clean_up(dag_id, execution_date, session=None):

    try:

        search = pendulum.strptime(execution_date, "%Y-%m-%dT%H:%M:%S")

        execution_date = execution_date.replace('T', ' ')

        r_config = json.loads(Variable.get("r_config"))
        if dag_id in r_config:
            exec_dates = r_config[dag_id]
            if execution_date in exec_dates:
                exec_dates.remove(execution_date)
                r_config[dag_id] = exec_dates

            if len(r_config[dag_id]) == 0:
                del r_config[dag_id]
        if len(r_config) != 0:
            Variable.set(
                key="r_config",
                value=json.dumps(r_config)
            )
        else:
            Variable.delete('r_config')

        # update airflow meta-database
        session.query(FailedDagRun).filter(FailedDagRun.dag_id == dag_id, FailedDagRun.execution_date.like(search))\
            .update({'state': 'recovery_executed'}, synchronize_session='fetch')

    except Exception as e:
        LoggingMixin().log.error(e)