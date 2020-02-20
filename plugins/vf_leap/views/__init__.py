#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from plugins.vf_leap.modals.recovery_modals import DagRunModel
from airflow.settings import Session
from plugins.vf_leap.views.recovery_dashboard_view import RecoveryDashboard


RECOVERY_DASHBOARD = RecoveryDashboard(model=DagRunModel,session=Session,name="Failed DAGs")
