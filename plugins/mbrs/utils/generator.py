#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

import inspect
from airflow import configuration
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.models.connection import Connection
from airflow.models.variable import Variable
from airflow.hooks.base_hook import BaseHook
from airflow import settings
from airflow import models
from plugins.mbrs.utils.dates import get_start_date
from airflow.exceptions import AirflowConfigException
from plugins.mbrs.utils.exceptions import AirflowException
from plugins.mbrs.utils.exceptions import ServiceNowConnectionNotFoundException
from plugins.mbrs.utils.exceptions import S3ConnectionNotFoundException
from plugins.mbrs.utils.exceptions import ConfigVariableNotFoundException
from plugins.mbrs.utils.exceptions import AirflowAPICredentialsNotFoundException
from plugins.mbrs.utils.exceptions import SFTPConnectionNotFoundException
from plugins.mbrs.utils.exceptions import StorageTypeNotFoundException
from plugins.mbrs.utils.exceptions import InvalidStorageTypeException
from plugins.mbrs.utils.exceptions import DropboxConnectionNotFoundException
from plugins.mbrs.modals.recovery_modals import Dags

from jinja2 import Template
import json
import os
import requests
import socket

bootstrap = False

servicenow_default = None
rest = None
config = None
r_config = None
dag_creation_dates = None
storage_type = None
sftp_default = None
s3_default = None
dropbox_default = None
new_dags = None


def create_airflow_connection_default_servicenow():

    session = settings.Session()

    if len(session.query(Connection).filter(Connection.conn_id == 'servicenow_default').all()) == 0:
        connection = Connection(
            conn_id='servicenow_default',
            host='https://dev1234.service-now.com',
            login='admin',
            password='password'
        )

        session.add(connection)
        session.commit()
        session.close()
        LoggingMixin().log.info("conn_id 'servicenow_default' initialized")


def create_airflow_connection_s3_default():
    session = settings.Session()

    if len(session.query(Connection).filter(Connection.conn_id == 's3_default').all()) == 0:
        connection = Connection(
            conn_id='s3_default',
            login='<access_key>',
            password='password',
            extra='{"region-name":"ap-south-1","bucket-name":"mini-brs"}'
        )

        session.add(connection)
        session.commit()
        session.close()
        LoggingMixin().log.info("conn_id 's3_default' initialized")


def create_airflow_connection_dropbox_default():
    session = settings.Session()

    if len(session.query(Connection).filter(Connection.conn_id == 'dropbox_default').all()) == 0:
        connection = Connection(
            conn_id='dropbox_default',
            login='<access_key>',
            password='password'
        )

        session = settings.Session()
        session.add(connection)
        session.commit()
        session.close()
        LoggingMixin().log.info("conn_id 'dropbox_default' initialized")


def create_airflow_rest_connection():

    from airflow.contrib.auth.backends.password_auth import PasswordUser
    import base64
    import os

    session = settings.Session()
    exists = session.query(models.User).filter(models.User.username == 'application').scalar()

    if exists is None:

        LoggingMixin().log.info("creating 'application' user for mini-BRS...")

        # create 'application' user

        random_key = str(base64.urlsafe_b64encode(os.urandom(32)))
        user = PasswordUser(models.User())
        user.username = 'application'
        user.email = 'application@nowhere.com'
        user.password = random_key
        session.add(user)
        session.commit()
        session.close()

        # create 'application' airflow connection
        rest = Connection(
            conn_id='rest',
            login='application',
            password=random_key
        )

        session = settings.Session()
        session.add(rest)
        session.commit()
        session.close()

        # create 'admin' user
        # admin_password = str(base64.urlsafe_b64encode(os.urandom(32)))

        config_parser = configuration.AirflowConfigParser()

        config_parser.read(
            configuration.get_airflow_config(
                        configuration.get_airflow_home()
                    )
        )

        u = config_parser.get(
            section='core',
            key='username'
        )

        p = config_parser.get(
            section='core',
            key='password'
        )

        user = PasswordUser(models.User())
        user.username = u
        user.email = 'admin@admin.com'
        user.password = p
        user.superuser = True
        session = settings.Session()
        session.add(user)
        session.commit()
        session.close()

        config_parser.remove_option(
            section='core',
            option='username'
        )

        config_parser.remove_option(
            section='core',
            option='password'
        )

        file = open(configuration.get_airflow_config(configuration.get_airflow_home()), 'w')

        config_parser.write(file)

        file.close()


def create_configuration_variables():

    # 'config' variable

    Variable.set(
        key='config',
        value=json.dumps({
            "tables": [],
            "start_date": "1da",
            "frequency": "hourly",
            "threshold": 10000,
            "export_format": "xml",
            "storage_type": "sftp",
            "email": ""
        }))

    # 'r_config' variable

    Variable.set(
        key='r_config',
        value='{}'
    )

    # 'dag_creation_dates' variable

    Variable.set(
        key='dag_creation_dates',
        value=json.dumps({})
    )


def ini():

    global bootstrap

    _trace_ = inspect.stack()
    _invoking_function_ = _trace_[len(_trace_)-2].function

    if _invoking_function_ == "initdb" or _invoking_function_ == "resetdb":

        LoggingMixin().log.info("airflow db initialization, starting bootstrap...")

        bootstrap = True

        # To Be Removed in subsequent release

        # create_airflow_connection_default_servicenow()
        #
        # create_configuration_variables()
        # create_airflow_connection_s3_default()
        # create_airflow_connection_dropbox_default()

    elif _invoking_function_ == "wrapper":

        LoggingMixin().log.info('mini-BRS running...')
        bootstrap = False
        create_airflow_rest_connection()

    else:
        pass

    return bootstrap


def create_dags():

    global dag_creation_dates
    global new_dags
    global email_notify_required

    new_dags = []

    dag_creation_dates = json.loads(Variable.get(key='dag_creation_dates'))
    email_notify_required = is_email_notification_required()

    try:
        for table in config.get('tables'):
            with open(configuration.get_airflow_home() + '/dags/templates/main.py.jinja2') as file_:
                template = Template(file_.read())

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
                    'start_date': start_date,
                    'email_required': email_notify_required
                }
            )

            with open(configuration.get_airflow_home() + '/dags/generated/dag_'
                      + '{}'.format(table).replace(' ', '_') + '.py', 'w') as f:
                f.write(output)
                new_dags.append('dag_' + '{}'.format(table).replace(' ', '_') + '.py')

        if len(r_config) != 0:

            for table in r_config:
                for exec_date in r_config.get(table):
                    execution_date = str(exec_date).replace(' ', 'T')[0:19]
                    with open(configuration.get_airflow_home()
                              + '/dags/templates/recovery_template.py.jinja2') as file_:
                        template = Template(file_.read())
                        output = template.render(
                            data={'dag_id': table, 'frequency': config.get('frequency'), 'storage_type': storage_type,
                                  'execution_date': execution_date})
                    with open(configuration.get_airflow_home() + '/dags/generated/r_dag_' + '{}_{}'.format(
                            table, execution_date).replace(' ', '_') + '.py', 'w') as f:
                        f.write(output)
                        e = '{}'.format(execution_date).replace(' ', 'T')
                        new_dags.append('r_dag_' + '{}_{}'.format(table, e).replace(' ', '_') + '.py')

        md_dag_ids = settings.Session.query(Dags.dag_id, Dags.fileloc).all()

        for record in md_dag_ids:
            (d_id, loc) = record
            filename = loc[str(loc).rfind('/') + 1:]
            if filename == 'dag_generator.py' or filename == 'dag_cleanup.py':
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
                        auth=(rest.login, rest.password)
                    )

                    dag_creation_dates.pop(d_id)

                except Exception as e:
                    LoggingMixin().log.error(str(e))

        Variable.set(key='dag_creation_dates', value=json.dumps(dag_creation_dates))

    except AirflowException:

        raise ConfigVariableNotFoundException()


def remove_dags():
    pass


def is_servicenow_default_connection_available():

    global servicenow_default

    try:
        servicenow_default = BaseHook.get_connection('servicenow_default')
        return True
    except AirflowException:
        raise ServiceNowConnectionNotFoundException('No ServiceNow Instance Registered !')


def is_rest_connection_available():

    global rest

    try:
        rest = BaseHook.get_connection('rest')
        return True
    except AirflowException:
        raise AirflowAPICredentialsNotFoundException("No Connection with conn_id 'rest' found !")


def is_config_variable_set():

    global config

    try:
        config = json.loads(Variable.get("config"))
        return True
    except KeyError:
        raise ConfigVariableNotFoundException("Variable 'config' not found")


def is_recovery_variable_set():

    global r_config

    try:
        r_config = json.loads(Variable.get("r_config"))
        return True
    except KeyError:
        raise ConfigVariableNotFoundException("Variable 'r_config' not found")


def is_storage_defined():

    global storage_type
    global sftp_default
    global s3_default
    global dropbox_default

    try:

        storage_type = str(config['storage_type']).lower()

        if storage_type == 'sftp':

            try:
                sftp_default = BaseHook.get_connection('sftp_default')

            except AirflowException:

                raise SFTPConnectionNotFoundException()

        elif storage_type == 's3':
            try:
                s3_default = BaseHook.get_connection('s3_default')

            except AirflowException:

                raise S3ConnectionNotFoundException()

        elif storage_type == 'dropbox':

            try:
                dropbox_default = BaseHook.get_connection('dropbox_default')

            except AirflowException:

                raise DropboxConnectionNotFoundException()
        else:

            raise InvalidStorageTypeException()

    except KeyError:

        raise StorageTypeNotFoundException


def is_email_notification_required():

    try:
        configuration.get(
            section='smtp',
            key='smtp_user'
        )
        configuration.get(
            section='smtp',
            key='smtp_password'
        )

        return True
    except AirflowConfigException:
        return False
