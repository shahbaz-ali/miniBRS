from airflow.hooks.S3_hook import S3Hook
import boto3
from botocore.exceptions import ClientError


class S3HookWrapper(S3Hook):

    """
    This class is a Wrapper Class for S3Hook of airflow.hooks.S3_hook
    It is used to pass the acess_key and secret_key directly to the hook
    without registering them into the airflow connection's database table
    """

    def __init__(self,
                 aws_access_key_id=None,
                 aws_secret_key_id=None,
                 aws_session_token=None,
                 endpoint_url = None,
                 *args,**kwargs):

        super().__init__(*args,**kwargs)

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_key_id = aws_secret_key_id
        self.aws_session_token = aws_session_token
        self.endpoint_url = endpoint_url


    def _get_credentials(self, region_name):
        """
        This method is overriding _get_credentials() method of Aws_hook
        which is the base class for S3Hook
        :param region_name: specify the region name
        :return: returns a boto3.session object with the specified aws_key,aws_secret and token
        """

        return boto3.session.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_key_id,
            aws_session_token=self.aws_session_token,
            region_name=region_name), self.endpoint_url


    def _check_aws_credentails(self):
        client = boto3.client(
            's3',
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_key_id,
        )

        try:
            response = client.list_buckets()

            if 'Buckets' in response:
                return True
            else:
                return False

        except ClientError as e:
            return False
