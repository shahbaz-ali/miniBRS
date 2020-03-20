#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow import DAG
from airflow.models.variable import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from plugins.mbrs.utils.exceptions import ConfigVariableNotFoundException
from datetime import datetime

with DAG(
    dag_id='dag_cleanup',
    description='This is responsible for cleaning the recovery dags generated for failed dag entries',
    schedule_interval='@daily',
    start_date=datetime(2020, 3, 19, 0, 0, 0),
    catchup=False,
    default_args={
        'owner': 'BRS'
    }
) as dag:

    def delete_r_config():

        try:
            Variable.set('r_config', '{}')
        except KeyError:
            raise ConfigVariableNotFoundException("Variable 'r_config' not found !")


    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    remove_recovery_dags = PythonOperator(
        task_id='cleanup',
        python_callable=delete_r_config
    )

    start >> remove_recovery_dags >> end
