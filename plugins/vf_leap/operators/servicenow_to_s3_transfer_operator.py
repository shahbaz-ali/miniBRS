from airflow.operators.bash_operator import BaseOperator


class ServiceNow2S3TransferOperator(BaseOperator):

    def execute(self, context):
        print('Hello World')