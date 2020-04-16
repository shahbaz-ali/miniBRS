#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

from airflow import DAG
from airflow import configuration
from airflow.models.variable import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from plugins.mbrs.utils.exceptions import ConfigVariableNotFoundException
from datetime import datetime
import shutil
import os
import json

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


    def delete_system_generated_tmp_files():
        config = json.loads(Variable.get(key='config'))
        tables = config['tables']
        tmp_path = "{}/{}".format(configuration.get_airflow_home(), 'backup/ServiceNow')
        for file in os.listdir(path=tmp_path):
            if file not in tables:
                shutil.rmtree('{}/{}'.format(tmp_path, file))
            else:
                data_dir = "{}/{}".format(tmp_path, file)
                for xml in os.listdir(path=data_dir):
                    expression = str(datetime.date(datetime.now()))
                    if not xml.__contains__(expression):
                        os.remove("{}/{}".format(data_dir, xml))


    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    remove_recovery_dags = PythonOperator(
        task_id='remove_recovery_dags',
        python_callable=delete_r_config
    )

    delete_system_generated_tmp_files = PythonOperator(
        task_id='remove_tmp_files',
        python_callable=delete_system_generated_tmp_files
    )

    start >> [remove_recovery_dags, delete_system_generated_tmp_files] >> end
