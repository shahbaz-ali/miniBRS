#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : MAK


from plugins.vf_leap.operators.common.servicenow_to_generic_transfer_operator import ServiceNowToGenericTransferOperator
from plugins.vf_leap.utils.exceptions import SFTPConnectionNotFoundException
import paramiko,socket
from airflow.hooks.base_hook import BaseHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.exceptions import AirflowException
from airflow import configuration
from datetime import datetime

class ServiceNowToSFTPTransferOperator(ServiceNowToGenericTransferOperator):
    """
    This method overrides the upload method of ServiceNowToGenericTransferOperator
    and provides an implementation of  uploading the generated file to SFTP server
    """

    def _upload(self,context):
        try:
            credentials_sftp = BaseHook.get_connection(self.storage_conn_id)
            self.sftp_user = credentials_sftp.login
            self.sftp_password = credentials_sftp.password
            self.sftp_host = credentials_sftp.host
        except AirflowException as e:
            raise SFTPConnectionNotFoundException


        l_file_path = self.file_name.replace('.csv', '.json')
        file_name = l_file_path[l_file_path.rfind('/') + 1:]

        paramiko.util.log_to_file(configuration.get('leap_core', 'project_folder') + "/logs/paramiko.log")

        # Open a transport
        transport = paramiko.Transport((self.sftp_host, 22))

        # Auth
        transport.connect(None, self.sftp_user, self.sftp_password)

        # Go!
        sftp = paramiko.SFTPClient.from_transport(transport)

        dt_current = datetime.now()

        r_file_path = '{}/{}/{}/{}/{}'.format(
            'vf_leap',
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
        if sftp: sftp.close()
        if transport: transport.close()
