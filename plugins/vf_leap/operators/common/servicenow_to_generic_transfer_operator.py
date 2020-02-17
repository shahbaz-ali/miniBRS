#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : MAK

from airflow.operators.bash_operator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.plugins_manager import AirflowPlugin
from airflow.hooks.base_hook import BaseHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.models import Variable
from airflow.exceptions import AirflowException
import json, os, requests,pytz
from plugins.vf_leap.hooks.servicenow_hook import ServiceNowHook
from plugins.vf_leap.utils.servicenow_client import ServiceNowHibernateException, ServiceNowAPIException
from datetime import datetime, timedelta
from airflow import configuration
from traceback import print_exc

class ServiceNowToGenericTransferOperator(BaseOperator):

    FREQUENCY = 'hourly'
    DIR_BACKUP_PATH = configuration.get('leap_core', 'project_folder') + '/backup/'

    @apply_defaults
    def __init__(
            self,
            snow_id,
            config,
            table,
            sftp_conn_id,
            snow_login = None,
            snow_password = None,
            snow_host = None,
            count_of_records = None,
            file_name = None,
            sftp_host = None,
            sftp_user = None,
            sftp_password = None,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.snow_id = snow_id
        self.config = config
        self.table = table
        self.sftp_conn_id = sftp_conn_id

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
            LoggingMixin().log.error("No Connection Found for ServiceNow Instance !")

        try:
            # Load Configuration Data
            self.config = json.loads(Variable.get(self.config))
            self.FREQUENCY = self.config['frequency']
        except KeyError as e:
            LoggingMixin().log.error("No configuration found !")

        # calculate time period of backup
        if(self.FREQUENCY == 'hourly'):
            freq_param = timedelta(hours=-1)

        elif(self.FREQUENCY == 'daily'):
            freq_param = timedelta(days =-1)
        else:
            freq_param = timedelta(hours=-1)
        time_now = datetime.now()
        timezone = pytz.timezone("Etc/UTC")
        self.to_time = timezone.localize(time_now)
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
        try:
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

        except ServiceNowHibernateException as e:
            self.count_of_records = 0
            LoggingMixin().log.warning("%s service now instance is hibernated !", str(self.snow_host))
            return None

        except ServiceNowAPIException as e:
            self.count_of_records = 0
            LoggingMixin().log.warning("%s service now api error !", str(self.snow_host))
            return None

        except Exception as e:
            self.count_of_records = 0
            LoggingMixin().log.error("%s service now error ! ", str(self.snow_host))
            LoggingMixin().log.error("%s", str(print_exc()))
            return None


    def execute(self,context):
        self._get_records(context)
        self._upload(context)
