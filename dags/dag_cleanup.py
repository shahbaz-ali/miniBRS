#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

"""
DAG_ID  : dag_cleanup
Purpose : This Dag is used to free storage space
Actions :
    - This DAG removes scheduled recovery dags
    - This DAG removes generated temporary data files
    - This DAG removes past logs and keeps current logs only

Scheduled : on daily basis at mid-night
"""


from datetime import datetime, timedelta
import shutil
import os
import json
from airflow import DAG
from airflow import configuration
from airflow.models.variable import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.log.logging_mixin import LoggingMixin
from plugins.mbrs.utils.exceptions import ConfigVariableNotFoundException


DOCUMENTATION = """
### Documentation
* **DAG_ID  :**
    - dag_cleanup
* **Purpose :**
    * This Dag is used to free storage space
* **Actions :**
    - This DAG removes scheduled recovery dags
    - This DAG removes generated temporary data files
    - This DAG removes past logs and keeps current logs only

* **Scheduled :**
    * on daily basis at mid-night
"""

with DAG(
        dag_id='dag_cleanup',
        description="This DAG free's storage space",
        schedule_interval='@daily',
        start_date=datetime(2020, 3, 19, 0, 0, 0),
        catchup=False,
        default_args={
            'owner': 'BRS'
        }
) as dag:

    def delete_r_config():
        """
        This function is used to delete the `r_config` variable
        :return: None
        """

        try:
            Variable.set('r_config', '{}')
        except KeyError:
            raise ConfigVariableNotFoundException("Variable 'r_config' not found !")


    def delete_system_generated_tmp_files():
        """
        This function deletes the generated temporary data files,
        And free's space
        :return: None
        """
        config = json.loads(Variable.get(key='config'))
        tables = config['tables']
        tmp_path = f"{configuration.get_airflow_home()}/backup/ServiceNow"
        for file in os.listdir(path=tmp_path):
            if file not in tables:
                shutil.rmtree(f'{tmp_path}/{file}')
            else:
                data_dir = f"{tmp_path}/{file}"
                for xml in os.listdir(path=data_dir):
                    expression = str(datetime.date(datetime.now()))
                    if not xml.__contains__(expression):
                        os.remove(f"{data_dir}/{xml}")

    def on_modification_limit_basis(path) -> bool:
        """
        This is a helper function used to determine, whether
        a file should be deleted on modified time basis. if modified
        time of file is one day ago it returns True ele False
        :param path:
        :type : str
        :return: bool
        """
        modified_time = datetime.fromtimestamp(os.path.getmtime(path))
        if modified_time < datetime.now() - timedelta(days=1):
            return True
        return False

    def on_size_limit_basis(path) -> bool:
        """
        This is a helper function used to determine, whether
        a file should be deleted on file_size limit basis, if
        the size of file is exceeding 10MB it returns True else
        False
        :param path:
        :type : str
        :return: bool
        """
        if os.path.getsize(path) >= 1000000000:
            return True
        return False

    def delete_airflow_logs(path=None):
        """
        This function is used to delete the logs based
        on modified_time check and file size limit check
        :return: None
        """
        if path is None:
            logs = f"{configuration.get_airflow_home()}/logs"
            files = os.listdir(logs)
        else:
            logs = path
            files = os.listdir(path)

        for file in files:
            path = f"{logs}/{file}"
            try:
                if os.path.isfile(path):
                    if on_modification_limit_basis(path) or on_size_limit_basis(path):
                        os.remove(path)
                else:
                    if on_modification_limit_basis(path):
                        shutil.rmtree(path)

                    else:
                        delete_airflow_logs(path)
            except FileNotFoundError:
                LoggingMixin().log.warning(f"{path} File not Found !")


    START = DummyOperator(task_id='start')
    END = DummyOperator(task_id='end')
    REMOVE_RECOVERY_DAGS = PythonOperator(
        task_id='remove_recovery_dags',
        python_callable=delete_r_config
    )

    DELETE_SYSTEM_GENERATED_TEMP_FILES = PythonOperator(
        task_id='remove_tmp_files',
        python_callable=delete_system_generated_tmp_files
    )

    PURGE_LOGS = PythonOperator(
        task_id='purge_logs',
        python_callable=delete_airflow_logs
    )

    START >> [REMOVE_RECOVERY_DAGS, DELETE_SYSTEM_GENERATED_TEMP_FILES, PURGE_LOGS] >> END


# DAG Documentation

dag.doc_md = DOCUMENTATION
