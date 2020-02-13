from airflow.plugins_manager import AirflowPlugin

from plugins.vf_leap.operators.servicenow_to_s3_transfer_operator import ServiceNow2S3TransferOperator
class VFLEAP(AirflowPlugin):
    name = 'VFLEAP'
    hooks = []
    operators = [ServiceNow2S3TransferOperator]
    executors = []
    macros = []
    menu_links = []