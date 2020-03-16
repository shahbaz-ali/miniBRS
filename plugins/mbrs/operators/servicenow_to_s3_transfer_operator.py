#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali,MAK

from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import S3ConnectionNotFoundException
from airflow.hooks.base_hook import BaseHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.exceptions import AirflowException
from airflow import configuration
from datetime import datetime
from plugins.mbrs.hooks.amazon_s3_hook import S3HookWrapper
from botocore.exceptions import ClientError

class ServiceNowToS3TransferOperator(ServiceNowToGenericTransferOperator):

    def _upload(self,context):

        try:
            # Load S3 storage_credentials
            credentials_s3 = BaseHook.get_connection(self.storage_conn_id)
        except AirflowException as e:
            raise S3ConnectionNotFoundException()

        dt_current = datetime.strptime(self.execution_date[:19], "%Y-%m-%dT%H:%M:%S")
        l_file_path = self.file_name.replace('.csv', '.json')
        file_name = l_file_path[l_file_path.rfind('/') + 1:]

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

        try:
            s3_hook = S3HookWrapper(
                aws_secret_key_id=credentials_s3.login,
                aws_access_key_id=credentials_s3.password
            )

            if s3_hook._check_aws_credentails():
                if not s3_hook.check_for_bucket(bucket_name='vf-leap'):
                    s3_hook.create_bucket(bucket_name='vf-leap', region_name=self.region_name)

            else:
                LoggingMixin().log.warning("Authentication Error : invalid s3 credentials")

            s3_hook.load_file(key=r_file_path, filename=self.l_file_path, bucket_name='vf-leap', replace=True)

        except (Exception, ClientError) as e:
            if isinstance(e, ClientError) and e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                return True
            else:
                LoggingMixin().log.error("error in AmazonS3 connection")
