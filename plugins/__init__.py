import sys
from airflow import configuration
sys.path.append(configuration.get('leap_core','project_folder'))
