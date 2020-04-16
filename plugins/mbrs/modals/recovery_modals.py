#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

from airflow.models.dagrun import DagRun
from airflow.models.variable import Variable
from airflow.models.dag import DagModel

class FailedDagRun(DagRun):
    """
        DagRun describes an instance of a Dag. It can be created
        by the scheduler (for regular runs) or by an external trigger
        """
    __tablename__ = "dag_run"


class Reason(Variable):
    pass


class Dags(DagModel):
    pass