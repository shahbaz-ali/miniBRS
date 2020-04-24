#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

"""
This is an abstract DAG, responsible for
generating user DAGs dynamically using a `config` variable
from the Airflow meta-database
"""

from airflow import DAG  # required
from plugins.mbrs.utils import generator


if not generator.ini():
    generator.is_servicenow_default_connection_available()
    generator.is_rest_connection_available()
    generator.is_config_variable_set()
    generator.is_storage_defined()
    generator.is_recovery_variable_set()
    generator.create_dags()
