#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow.models.dagrun import DagRun

class DagRunModel(DagRun):
    """
        DagRun describes an instance of a Dag. It can be created
        by the scheduler (for regular runs) or by an external trigger
        """
    __tablename__ = "dag_run"
