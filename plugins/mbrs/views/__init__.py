#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from plugins.mbrs.modals.recovery_modals import FailedDagRun,Reason
from airflow.settings import Session
from plugins.mbrs.views.recovery_dashboard_view import RecoveryDashboard,TaskInstanceFailureVariable


RECOVERY_DASHBOARD = RecoveryDashboard(model=FailedDagRun,session=Session,name="Failed DAGs",endpoint='failed')
DEMO_VIEW = TaskInstanceFailureVariable(model=Reason,session=Session,name="Reason",endpoint='task_fail_reason')