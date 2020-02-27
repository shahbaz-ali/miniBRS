#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow.operators.python_operator import PythonOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.email import send_email
from airflow.models.variable import Variable
from plugins.vf_leap.utils.exceptions import ConfigVariableNotFoundException
import json

class Email_Operator(PythonOperator):

    @apply_defaults
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)


    def execute(self, context):

        (fetch_record_count,send_data_to_submission,)= context['ti'].xcom_pull(
            key='exception',
            task_ids=('fetch_record_count', 'send_data_to_submission')
        )


        if fetch_record_count is None:
            message = '<img src="https://airflow.apache.org/images/feature-image.png" width="400" height="100"/>' \
                      '<h2>AIRFLOW TASK FAILURE:</h2><hr/>' \
                      '<strong>DAG : </strong>    {} <br/><hr/>' \
                      '<strong>TASKS:</strong>  {}<br/><hr/>' \
                      '<strong>Reason:</strong> {}<br/><hr/>' \
                .format(self.dag_id, 'send_data_to_submission', send_data_to_submission)
        elif send_data_to_submission is None:
            message = '<img src="https://airflow.apache.org/images/feature-image.png" width="400" height="100"/>' \
                      '<h2>AIRFLOW TASK FAILURE:</h2><hr/>' \
                      '<strong>DAG : </strong>    {} <br/><hr/>' \
                      '<strong>TASKS:</strong>  {}<br/><hr/>' \
                      '<strong>Reason:</strong> {}<br/><hr/>' \
                .format(self.dag_id, 'fetch_record_count', fetch_record_count)

        try:
            config = json.loads(Variable.get("config"))
            email = config['email']
        except NameError as e:
            raise ConfigVariableNotFoundException()

        send_email(
            to=email,
            subject='Airflow Notification',
            html_content=message
        )