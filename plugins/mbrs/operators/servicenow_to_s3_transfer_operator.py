#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali,MAK

from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import S3ConnectionNotFoundException
from airflow.hooks.base_hook import BaseHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.exceptions import AirflowException
from airflow import configuration
from datetime import datetime, timedelta
from plugins.mbrs.hooks.amazon_s3_hook import S3HookWrapper
from botocore.exceptions import ClientError
import json

class ServiceNowToS3TransferOperator(ServiceNowToGenericTransferOperator):

    def _upload(self,context):

        try:
            # Load S3 storage_credentials
            credentials_s3 = BaseHook.get_connection(self.storage_conn_id)
        except AirflowException as e:
            raise S3ConnectionNotFoundException()

        dt_current = datetime.strptime(self.execution_date[:19], "%Y-%m-%dT%H:%M:%S")
        self.l_file_path = self.file_name
        index = self.l_file_path.rfind('/')
        file_name = self.l_file_path[index + 1:]

        exec_hour = str(dt_current.hour)
        exec_minute = str(dt_current.minute)
        exec_second = str(dt_current.second)

        if exec_hour == '0' and exec_minute == '0' and exec_second == '0':
            dt_current = dt_current - timedelta(days=1)
            r_file_path = '{}/{}/{}/{}/{}'.format(
                '/mbrs',
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
                '/mbrs',
                'Servicenow',
                self.table,
                '{}-{}-{}'.format(
                    dt_current.year,
                    dt_current.month,
                    dt_current.day
                ),
                file_name)

        try:
            s3_hook = S3HookWrapper(
                aws_secret_key_id=credentials_s3.password,
                aws_access_key_id=credentials_s3.login
            )

            if s3_hook._check_aws_credentails():
                bucket_name = json.loads(credentials_s3.get_extra())["bucket-name"]
                if not s3_hook.check_for_bucket(bucket_name=bucket_name):
                    region_name = json.loads(credentials_s3.get_extra())["region-name"]
                    s3_hook.create_bucket(bucket_name=bucket_name, region_name=region_name)

            else:
                LoggingMixin().log.warning("Authentication Error : invalid s3 credentials")
            s3_hook.load_file(filename=self.l_file_path, key=r_file_path, bucket_name=bucket_name, replace=True)

        except (Exception, ClientError) as e:
            if isinstance(e, ClientError) and e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                return True

            raise
