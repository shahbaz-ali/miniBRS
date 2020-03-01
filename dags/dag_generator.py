#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow import DAG
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.hooks.base_hook import BaseHook
from airflow.settings import Session
from airflow.models import Variable
from plugins.vf_leap.utils.exceptions import AirflowException, ServiceNowConnectionNotFoundException, \
    S3ConnectionNotFoundException, ConfigVariableNotFoundException, AirflowAPICredentialsNotFoundException, \
    SFTPConnectionNotFoundException, StorageTypeNotFoundException, \
    InvalidStorageTypeException, DropboxConnectionNotFoundException
from plugins.vf_leap.modals.recovery_modals import Dags
import json, os, requests
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
    raise ConfigVariableNotFoundException()

try:
    # Load recovery Configuration Data
    r_config = json.loads(Variable.get("r_config"))
    if len(r_config) > 0:
        is_recovery = True
except KeyError as e:
    pass

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
        # dropbox Connection details
        try:
            credentials_dropbox = BaseHook.get_connection('dropbox_default')
            is_storage_available = True
        except AirflowException as e:
            raise DropboxConnectionNotFoundException()
    else:
        raise InvalidStorageTypeException()

except KeyError as e:
    raise StorageTypeNotFoundException

dag = DAG(
    dag_id='dag_generator',
    description='Generates DAG corresponding to a specific table',
    schedule_interval=None,
    start_date=datetime(2020, 11, 1),
    catchup=False
)

if (
        is_configuration_available and is_storage_available and is_rest_available and is_servicenow_available and not is_recovery):
    new_dags = []

    try:
        for table in config.get('tables'):
            with open(os.path.dirname(os.path.realpath(__file__)) + '/templates/main.py.jinja2') as file_:
                template = Template(file_.read())
            output = template.render(
                data={'dag_id': table, 'frequency': config.get('frequency'), 'storage_type': storage_type})

            with open(os.path.dirname(os.path.realpath(__file__)) + '/generated/dag_' + '{}'.format(table).replace(' ',
                                                                                                                   '_') + '.py',
                      'w') as f:
                f.write(output)
                new_dags.append('dag_' + '{}'.format(table).replace(' ', '_') + '.py')
    except AirflowException as e:
        raise ConfigVariableNotFoundException()

    md_dag_ids = Session.query(Dags.dag_id,Dags.fileloc).all()

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
                    url="http://localhost:8080/api/experimental/dags/{}".format(str(d_id)),
                    auth=(api_login, api_passcode)
                )
            except Exception as e:
                LoggingMixin().log.error(str(e))
elif (
        is_configuration_available and is_storage_available and is_rest_available and is_servicenow_available and is_recovery):
    new_recovery_dags = []
    try:
        for table in r_config:
            for exec_date in r_config.get(table):
                execution_date = str(exec_date).replace(' ', 'T')[0:19]
                with open(os.path.dirname(os.path.realpath(__file__)) + '/templates/recovery_template.py.jinja2') as file_:
                    template = Template(file_.read())
                    output = template.render(
                        data={'dag_id': table, 'frequency': config.get('frequency'), 'storage_type': storage_type,
                              'execution_date': execution_date})
                    with open(os.path.dirname(os.path.realpath(__file__)) + '/generated/r_dag_' + '{}_{}'.format(
                            table,execution_date).replace(' ', '_') + '.py', 'w') as f:
                        f.write(output)
                        new_recovery_dags.append('r_dag_' + '{}'.format(table).replace(' ', '_') + '.py')
    except AirflowException as e:
        raise ConfigVariableNotFoundException()


else:
    LoggingMixin().log.error('missing connections and variables, please check your airflow configuration !')
