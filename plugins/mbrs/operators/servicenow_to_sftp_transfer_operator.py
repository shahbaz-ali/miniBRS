#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : MAK


from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import SFTPConnectionNotFoundException
import paramiko,socket
from airflow.hooks.base_hook import BaseHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.exceptions import AirflowException
from airflow import configuration
from datetime import datetime,timedelta


class ServiceNowToSFTPTransferOperator(ServiceNowToGenericTransferOperator):
    """
    This method overrides the upload method of ServiceNowToGenericTransferOperator
    and provides an implementation of  uploading the generated file to SFTP server
    """

    def _upload(self, context):
        try:
            credentials_sftp = BaseHook.get_connection(self.storage_conn_id)
            self.sftp_user = credentials_sftp.login
            self.sftp_password = credentials_sftp.password
            self.sftp_host = credentials_sftp.host
        except AirflowException as e:
            raise SFTPConnectionNotFoundException

        l_file_path = self.file_name
        file_name = l_file_path[l_file_path.rfind('/') + 1:]

        paramiko.util.log_to_file(configuration.get_airflow_home()+ "/logs/paramiko.log")

        # Open a transport
        transport = paramiko.Transport((self.sftp_host, 22))

        # Auth
        transport.connect(None, self.sftp_user, self.sftp_password)

        # Go!
        sftp = paramiko.SFTPClient.from_transport(transport)

        dt_current = datetime.strptime(self.execution_date[:19], "%Y-%m-%dT%H:%M:%S")

        exec_hour = str(dt_current.hour)
        exec_minute = str(dt_current.minute)
        exec_second = str(dt_current.second)

        if exec_hour == '0' and exec_minute == '0' and exec_second == '0':
            dt_current = dt_current - timedelta(days=1)
            r_file_path = '{}/{}/{}/{}/{}'.format(
                'mbrs',
                'Servicenow',
                self.table,
                '{}-{}-{}'.format(
                    dt_current.year,
                    dt_current.month,
                    dt_current.day
                ),
                file_name)
        else:
            r_file_path = '{}/{}/{}/{}/{}'.format(
                'mbrs',
                'Servicenow',
                self.table,
                '{}-{}-{}'.format(
                    dt_current.year,
                    dt_current.month,
                    dt_current.day
                ),
                file_name)

        for dir in r_file_path.split('/')[:-1]:
            try:
                sftp.listdir(dir)
                sftp.chdir(dir)
            except IOError as e:
                sftp.mkdir(dir)
                sftp.chdir(dir)

        sftp.put(l_file_path, file_name)

        # Close
        if sftp:
            sftp.close()
        if transport:
            transport.close()
