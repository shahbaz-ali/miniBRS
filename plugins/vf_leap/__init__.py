
#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow.plugins_manager import AirflowPlugin

from plugins.vf_leap.operators.servicenow_to_s3_transfer_operator import ServiceNowToS3TransferOperator
from plugins.vf_leap.operators.servicenow_to_sftp_transfer_operator import ServiceNowToSFTPTransferOperator

from plugins.vf_leap.views import RECOVERY_DASHBOARD,DEMO_VIEW
#from plugins.vf_leap.blueprints import RECOVERY_BLUEPRINT


class VFLEAP(AirflowPlugin):
    name = 'VFLEAP'
    hooks = []
    operators = [ServiceNowToS3TransferOperator,ServiceNowToSFTPTransferOperator]
    executors = []
    macros = []
    menu_links = []
    admin_views = [RECOVERY_DASHBOARD,DEMO_VIEW]
    #flask_blueprints = [RECOVERY_BLUEPRINT]