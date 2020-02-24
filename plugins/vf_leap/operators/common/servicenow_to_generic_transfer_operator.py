#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : MAK

from airflow.operators.bash_operator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.models import Variable
from airflow.exceptions import AirflowException
import json, os,pendulum
from plugins.vf_leap.hooks.servicenow_hook import ServiceNowHook
from plugins.vf_leap.utils.exceptions import ServiceNowConnectionNotFoundException,ConfigVariableNotFoundException
from datetime import datetime, timedelta
from airflow import configuration

class ServiceNowToGenericTransferOperator(BaseOperator):

    template_fields = ('execution_date',)
    FREQUENCY = 'hourly'
    DIR_BACKUP_PATH = configuration.get('leap_core', 'project_folder') + '/backup/'

    @apply_defaults
    def __init__(
            self,
            snow_id,
            config,
            table,
            sftp_conn_id,
            execution_date = None,
            snow_login = None,
            snow_password = None,
            snow_host = None,
            count_of_records = None,
            file_name = None,
            sftp_host = None,
            sftp_user = None,
            sftp_password = None,
            *args, **kwargs) -> None:

        """
                Takes ServiceNow connection id named 'conn_id' (an Airflow Connection),
                Sftp connection id named 'sftp_conn_id' (an Airflow Connection),
                config named 'config' (an Airflow Variable)
                and servicenow table name


                :param snow_id: An Airflow Connection containing servicenow credentials username,password and host
                :param sftp_conn_id: An Airflow Connection containing SFTP credentials
                :param config: An Airflow variable containing confugration regarding servicenow instance like frequency,threshold etc
                :param table: ServiceNow table name from which data is to be fetched
                :type snow_id: str
                :type sftp_conn_id: str
                :type config: str
                :type table: str
                """

        super().__init__(*args, **kwargs)
        self.snow_id = snow_id
        self.config = config
        self.table = table
        self.sftp_conn_id = sftp_conn_id
        self.execution_date = execution_date


    def pre_execute(self,context):
        """
        This method gets servicenow login credentials from servicenow conn_id
        and loads config variable
        and calculates the actual time period for which data is to be fetched based on frequency in config.

        """
        # ServiceNow Connection details
        try:
            credentials_snow = BaseHook.get_connection(self.snow_id)
            self.snow_login = credentials_snow.login
            self.snow_password = credentials_snow.password
            self.snow_host = credentials_snow.host
        except AirflowException as e:
            raise ServiceNowConnectionNotFoundException

        try:
            # Load Configuration Data
            self.config = json.loads(Variable.get(self.config))
            self.FREQUENCY = self.config['frequency']
        except KeyError as e:
            raise ConfigVariableNotFoundException

        # calculate time period of backup
        if(self.FREQUENCY == 'hourly'):
            freq_param = timedelta(hours=-1)

        elif(self.FREQUENCY == 'daily'):
            freq_param = timedelta(days =-1)
        else:
            freq_param = timedelta(hours=-1)
        execution_datetime = datetime.strptime(self.execution_date[:-6], "%Y-%m-%dT%H:%M:%S")

        self.to_time = datetime(
            year=execution_datetime.year,
            month=execution_datetime.month,
            day=execution_datetime.day,
            hour=execution_datetime.hour,
            minute=execution_datetime.minute,
            second=execution_datetime.second,
            tzinfo=pendulum.timezone("UTC")
        )
        self.from_time = self.to_time + freq_param

    def _upload(self):

        """
        This method should be overridden by child class
        :return:
        :raises NotImplementedError

        """

        raise NotImplementedError


    def _get_records(self,context):
        """
        This method actually gets the data from a particular servicenow table for a particular time period
        and generates a file of it.

        """
        # Basic Authentication
        service_now_hook = ServiceNowHook(
            host=self.snow_host,
            login=self.snow_login,
            password=self.snow_password
        )
        rs = service_now_hook.api_call(
            route='{}{}'.format('/api/now/table/', self.table),
            query_params={
                'sysparm_query': "sys_updated_onBETWEENjavascript:gs.dateGenerate('{}','{}')@javascript:gs.dateGenerate('{}','{}')".format(
                    str(self.from_time.date()),
                    str(self.from_time.time()),
                    str(self.to_time.date()),
                    str(self.to_time.time())
                )
            }
        )
        LoggingMixin().log.warning("backup folder :" + self.DIR_BACKUP_PATH)
        l_dir_backup_path = "{}ServiceNow/{}/".format(self.DIR_BACKUP_PATH,
                                                      self.table
                                                      )

        bk_file_name = '{}_{}_{}.xml'.format(self.table, str(self.from_time), str(self.to_time))

        bk_file_path = l_dir_backup_path + bk_file_name

        r_file_path = l_dir_backup_path.replace(self.DIR_BACKUP_PATH, '/vf_leap/') + bk_file_name

        if not os.path.exists(l_dir_backup_path):
            os.makedirs(l_dir_backup_path)

        with open(bk_file_path, 'w') as bk:
            bk.write(rs)
        self.file_name = bk_file_path
        return bk_file_path


    def execute(self,context):
        self._get_records(context)
        self._upload(context)
