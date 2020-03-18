#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow import DAG
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.hooks.base_hook import BaseHook
from airflow.settings import Session
from airflow.models import Variable
from plugins.mbrs.utils.exceptions import AirflowException, ServiceNowConnectionNotFoundException, \
    S3ConnectionNotFoundException, ConfigVariableNotFoundException, AirflowAPICredentialsNotFoundException, \
    SFTPConnectionNotFoundException, StorageTypeNotFoundException, \
    InvalidStorageTypeException, DropboxConnectionNotFoundException
from plugins.mbrs.modals.recovery_modals import Dags
from plugins.mbrs.utils.dates import get_start_date
import json, os, requests,socket
from jinja2 import Template

from datetime import datetime

# flags

is_servicenow_available = False
is_storage_available = False
is_configuration_available = False
is_rest_available = False
is_recovery = False

# ServiceNow Connection details
try:
    credentials_snow = BaseHook.get_connection('servicenow_default')
    login = credentials_snow.login
    passcode = credentials_snow.password
    host = credentials_snow.host
    is_servicenow_available = True
except AirflowException as e:
    raise ServiceNowConnectionNotFoundException()

# Airflow API Connection details
try:
    credentials = BaseHook.get_connection('rest')
    api_login = credentials.login
    api_passcode = credentials.password
    is_rest_available = True
except AirflowException as e:
    raise AirflowAPICredentialsNotFoundException()

try:
    # Load Configuration Data
    config = json.loads(Variable.get("config"))
    is_configuration_available = True
except KeyError as e:

    Variable.set(
        key='config',
        value=json.dumps({
            "tables" : [],
            "start_date":"1da",
            "frequency" : "hourly",
            "threshold" : 10000,
            "export_format" : "xml",
            "storage_type" : "sftp",
            "email":""
        }))

try:
    # Load recovery Configuration Data
    r_config = json.loads(Variable.get("r_config"))
    if len(r_config) > 0:
        is_recovery = True
except KeyError as e:
    Variable.set(
        key='r_config',
        value='{}'
    )

# get storage Type from config
try:
    storage_type = config['storage_type']
    storage_type = str(storage_type).lower()

    if storage_type == 'sftp':

        try:
            # Load SFTP storage_credentials
            credentials_sftp = BaseHook.get_connection('sftp_default')
            is_storage_available = True
        except AirflowException as e:
            raise SFTPConnectionNotFoundException()

    elif storage_type == 's3':
        try:
            # Load S3 storage_credentials
            credentials_s3 = BaseHook.get_connection('s3_default')
            is_storage_available = True
        except AirflowException as e:
            raise S3ConnectionNotFoundException()

    elif storage_type == 'dropbox':

        try:
            credentials_dropbox = BaseHook.get_connection('dropbox_default')
            is_storage_available = True
        except AirflowException as e:
            raise DropboxConnectionNotFoundException()
    else:
        raise InvalidStorageTypeException()

except KeyError as e:
    raise StorageTypeNotFoundException

# dag creation dates
try:

    dag_creation_dates = json.loads(Variable.get(key='dag_creation_dates'))

except KeyError as e:

    Variable.set(
        key='dag_creation_dates',
        value=json.dumps({})
    )


dag = DAG(
    dag_id='dag_generator',
    description='Generates DAG corresponding to a specific table',
    schedule_interval=None,
    start_date=datetime(2020, 11, 1),
    catchup=False,
    default_args={
        'owner': 'BRS',
    }
)

if is_configuration_available and is_storage_available and is_rest_available and is_servicenow_available:

    new_dags = []

    try:
        for table in config.get('tables'):
            with open(os.path.dirname(os.path.realpath(__file__)) + '/templates/main.py.jinja2') as file_:
                template = Template(file_.read())

            dag_creation_dates = json.loads(Variable.get(key='dag_creation_dates'))

            if dag_creation_dates.get(table) is not None:
                start_date = dag_creation_dates.get(table)
            else:
                start_date = get_start_date(config.get('start_date'))
                dag_creation_dates[table] = str(start_date)

            output = template.render(
                data={
                    'dag_id': table,
                    'frequency': config.get('frequency'),
                    'storage_type': storage_type,
                    'start_date':start_date
                }
            )

            with open(os.path.dirname(os.path.realpath(__file__))
                      + '/generated/dag_' + '{}'.format(table).replace(' ', '_') + '.py', 'w') as f:
                f.write(output)
                new_dags.append('dag_' + '{}'.format(table).replace(' ', '_') + '.py')

        for table in r_config:
            for exec_date in r_config.get(table):
                execution_date = str(exec_date).replace(' ', 'T')[0:19]
                with open(os.path.dirname(os.path.realpath(__file__))
                          + '/templates/recovery_template.py.jinja2') as file_:
                    template = Template(file_.read())
                    output = template.render(
                        data={'dag_id': table, 'frequency': config.get('frequency'), 'storage_type': storage_type,
                              'execution_date': execution_date})
                with open(os.path.dirname(os.path.realpath(__file__)) + '/generated/r_dag_' + '{}_{}'.format(
                        table, execution_date).replace(' ', '_') + '.py', 'w') as f:
                    f.write(output)
                    e = '{}'.format(execution_date).replace(' ', 'T')
                    new_dags.append('r_dag_' + '{}_{}'.format(table, e).replace(' ', '_') + '.py')

    except AirflowException as e:
        raise ConfigVariableNotFoundException()

    md_dag_ids = Session.query(Dags.dag_id, Dags.fileloc).all()

    for record in md_dag_ids:
        (d_id, loc) = record
        filename = loc[str(loc).rfind('/') + 1:]
        if filename == 'dag_generator.py':
            continue
        if filename not in new_dags:
            try:
                if os.path.exists(str(loc)):
                    os.remove(str(loc))
                else:
                    LoggingMixin().log.warning("{} file doesn't exists !".format(filename))

                requests.delete(
                    url="http://{}:8080/api/experimental/dags/{}".format(
                        socket.gethostbyname(socket.gethostname()),
                        str(d_id)
                    ),
                    auth=(api_login, api_passcode)
                )

                dag_creation_dates.pop(d_id)
                
            except Exception as e:
                LoggingMixin().log.error(str(e))

    Variable.set(key='dag_creation_dates', value=json.dumps(dag_creation_dates))

else:

    LoggingMixin().log.error('missing connections and variables, please check your airflow configuration !')
