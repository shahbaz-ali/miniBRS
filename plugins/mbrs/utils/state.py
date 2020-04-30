#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com


'''
This is a modified implementation of airflow State class
'''

from airflow.utils.state import State

RECOVERY_EXECUTED = "recovery_executed"
State.RECOVERY_EXECUTED = "recovery_executed"
State.task_states + (RECOVERY_EXECUTED,)
State.dag_states + (RECOVERY_EXECUTED,)
State.state_color[RECOVERY_EXECUTED] = 'magenta'
