
#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow import DAG
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.hooks.base_hook import BaseHook
from airflow.hooks.sqlite_hook import SqliteHook
from airflow.models import Variable
from plugins.vf_leap.utils.exceptions import AirflowException,ServiceNowConnectionNotFoundException,\
    S3ConnectionNotFoundException,ConfigVariableNotFoundException,AirflowAPICredentialsNotFoundException,\
    SFTPConnectionNotFoundException,StorageTypeNotFoundException,\
    InvalidStorageTypeException,DropboxConnectionNotFoundException
import json,os,requests,pytz
from jinja2 import Template
from datetime import datetime, timedelta

from datetime import datetime


#flags

is_servicenow_available = False
is_storage_available = False
is_configuration_available = False
is_rest_available = False

#ServiceNow Connection details
try:
    credentials_snow = BaseHook.get_connection('snow_id')
    login = credentials_snow.login
    passcode = credentials_snow.password
    host = credentials_snow.host
    is_servicenow_available = True
except AirflowException as e:
    raise ServiceNowConnectionNotFoundException()

#Airflow API Connection details
try:
    credentials = BaseHook.get_connection('rest')
    api_login = credentials.login
    api_passcode = credentials.password
    is_rest_available = True
except AirflowException as e:
    raise AirflowAPICredentialsNotFoundException()


try:
    #Load Configuration Data
    config = json.loads(Variable.get("config"))
    is_configuration_available = True
except KeyError as e:
    raise ConfigVariableNotFoundException()

#get storage Type from config
try:
    storage_type = config['storage_type']

    if storage_type == 'SFTP':

        try:
            #Load SFTP storage_credentials
            credentials_sftp = BaseHook.get_connection('sftp_global')
            is_storage_available = True
        except AirflowException as e:
            raise SFTPConnectionNotFoundException()

    elif storage_type == 'S3':
        try:
            # Load S3 storage_credentials
            credentials_s3 = BaseHook.get_connection('s3_global')
            is_storage_available = True
        except AirflowException as e:
            raise S3ConnectionNotFoundException()


    elif storage_type == 'DROPBOX':
        # dropbox Connection details
        try:
            credentials_dropbox = BaseHook.get_connection('dropbox_global')
            is_storage_available = True
        except AirflowException as e:
            raise DropboxConnectionNotFoundException()
    else:
        raise InvalidStorageTypeException()

except KeyError as e:
    raise StorageTypeNotFoundException

# calculate time period of backup
time_now = datetime.now()
timezone = pytz.timezone("Etc/UTC")
to_time = timezone.localize(time_now)
from_time = to_time + timedelta(days=-1)

dag = DAG(
        dag_id='dag_generator',
        description='Generates DAG corresponding to a specific table',
        schedule_interval= None,
        start_date=datetime(2020, 11, 1),
        catchup=False
)



if (is_configuration_available and is_storage_available and is_rest_available and is_servicenow_available) :
    new_dags= []

    try:
        for table in config.get('tables'):

            with open(os.path.dirname(os.path.realpath(__file__)) + '/templates/main.py.jinja2') as file_:
                template = Template(file_.read())
            output = template.render(data={'dag_id':table,'frequency':config.get('frequency'),'storage_type':storage_type})

            with open(os.path.dirname(os.path.realpath(__file__))+ '/generated/dag_' + '{}'.format(table).replace(' ','_') + '.py', 'w') as f:
                f.write(output)
                new_dags.append('dag_' + '{}'.format(table).replace(' ','_') + '.py')
    except AirflowException as e:
        raise ConfigVariableNotFoundException()

    l_hook = SqliteHook(sqlite_conn_id = 'sqlite_default')
    connection = l_hook.get_conn()
    cursor = connection.cursor()

    cursor.execute("SELECT dag_id,fileloc FROM dag")
    md_dag_ids = cursor.fetchall()

    for record in md_dag_ids:
        (d_id,loc) = record
        filename = loc[str(loc).rfind('/')+1:]
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
                    auth=(api_login,api_passcode)
                )
            except Exception as e:
                LoggingMixin().log.error(str(e))

else:
    LoggingMixin().log.error('missing connections and variables, please check your airflow configuration !')