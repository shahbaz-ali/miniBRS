
'''
To test the total number of tasks in the DAG, upstream and downstream dependencies of each task etc.
'''

import pytest

from airflow.exceptions import AirflowConfigException
from airflow.models import DagBag
from airflow import configuration
from tests.ignores_warning import IgnoreWarnings

IgnoreWarnings.ignore()

def is_email_present():
        isPresent=False
        try:
            configuration.conf.get('smtp', 'smtp_user')
            isPresent = True
        except AirflowConfigException as e:
            isPresent=False

        return isPresent

class TestDAGDefnition():

    @pytest.fixture
    def dagbagDags(self):
        dagbag = DagBag(dag_folder=configuration.get_airflow_home()+'/dags/generated', include_examples=False)
        return dagbag.dags

    @pytest.fixture
    def dagbag(self):
        dagbag = DagBag(dag_folder=configuration.get_airflow_home() + '/dags/generated', include_examples= False)
        return dagbag

    #OK Py
    @pytest.mark.count_tasks
    def test_task_count_in_dag(self,dagbagDags,dagbag):
        """Check task count of a dag"""

        for dag_id, dag in dagbagDags.items():

            #dag_id='incident'
            dag = dagbag.get_dag(dag_id)
            number_of_tasks=len(dag.tasks)
            msg=f'Number of tasks are not same as expected in DAG with id  {dag_id}'

            if is_email_present():
                '''Total number of tasks in a dag will be 8'''
                assert number_of_tasks == 8, msg
            else:
                '''Without email operator total tasks will be 7'''
                assert number_of_tasks == 7, msg

    #OK Py
    @pytest.mark.email
    def test_is_email_task_present(self,dagbagDags):
        isPresent=False
        for dag_id, dag in dagbagDags.items():
            try:
                configuration.conf.get('smtp', 'smtp_user')
                isPresent = True
            except AirflowConfigException as e:
                isPresent=False
                msg= f'Email operator is not present in the DAG with id {dag_id}'

            assert isPresent == False ,msg

    #OK Py
    @pytest.mark.contain
    def test_contain_tasks(self,dagbagDags,dagbag):
        """Check task contains in a dag"""

        expected_tasks = ['start', 'end', 'fetch_record_count', 'count_within_threshold', 'count_exceeds_threshold', \
                          'count_is_zero', 'send_data_to_submission']

        if is_email_present():
            expected_tasks.append("notify_submission_failure")
        for dag_id, dag in dagbagDags.items():

           # dag_id='incident'
            dag = dagbag.get_dag(dag_id)
            tasks = dag.tasks
            task_ids = list(map(lambda task: task.task_id, tasks))
            task_ids=sorted(task_ids)
            expected_tasks=sorted(expected_tasks)
            msg=f'Tasks in DAG with id \'{dag_id}\' are not same as expected'
            assert task_ids == expected_tasks, msg

    #OK Py
    @pytest.mark.fetch_dependencies
    def test_dependencies_of_fetch_record_count_task(self,dagbagDags,dagbag):
        """Check the task dependencies of fetch_record_count in a dag"""

        for dag_id, dag in dagbagDags.items():

            #dag_id='incident'
            dag = dagbag.get_dag(dag_id)
            fetch_record_count_task = dag.get_task('fetch_record_count')

            upstream_task_ids = list(map(lambda task: task.task_id, fetch_record_count_task.upstream_list))
            expected_upstream_task=['start']
            msg=f'Upstream tasks of fetch_record_count in a DAG with id \'{dag_id}\' are not same as expected'
            assert upstream_task_ids == expected_upstream_task ,msg

            downstream_task_ids = list(map(lambda task: task.task_id, fetch_record_count_task.downstream_list))
            expected_downstream_task=['count_is_zero', 'count_within_threshold', 'count_exceeds_threshold']
            downstream_task_ids=sorted(downstream_task_ids)
            expected_downstream_task=sorted(expected_downstream_task)
            msg=f'DownStream tasks of fetch_record_count in a DAG with id \'{dag_id}\' are not same as expected'
            assert downstream_task_ids == expected_downstream_task, msg

    #OK Py
    @pytest.mark.submission
    def test_dependencies_of_send_data_to_submission_task(self,dagbagDags,dagbag):

        """Check the task dependencies of send_data_to_submission in incident dag"""
        for dag_id, dag in dagbagDags.items():

           # dag_id='incident'
            dag = dagbag.get_dag(dag_id)
            send_data_to_submission_task = dag.get_task('send_data_to_submission')

            upstream_task_ids = list(map(lambda task: task.task_id, send_data_to_submission_task.upstream_list))
            expected_upstream_task=['count_within_threshold']
            msg=f'Upstream tasks for task \'send_data_to_submission\' are not same as expected in DAG with id \'{dag_id}\''
            assert  upstream_task_ids == expected_upstream_task ,msg

            downstream_task_ids = list(map(lambda task: task.task_id, send_data_to_submission_task.downstream_list))
            expected_downstream_task=['end']
            if is_email_present():
                '''if email is present the downstream task of send_data_to_submission will be
                   notify_submission_failure, not the end task
                '''
                del expected_downstream_task[0]
                expected_downstream_task.append("notify_submission_failure")
                expected_downstream_task=sorted(expected_downstream_task)
            assert downstream_task_ids == expected_downstream_task, msg

    #OK Py
    @pytest.mark.end_dependencies
    def test_dependencies_of_end_task(self,dagbagDags,dagbag):

        """Check the task dependencies of end task in incident dag"""

        for dag_id, dag in dagbagDags.items():
            #dag_id='incident'
            dag = dagbag.get_dag(dag_id)
            end_task = dag.get_task('end')

            upstream_task_ids = list(map(lambda task: task.task_id, end_task.upstream_list))
            expected_upstream_task=['count_is_zero', 'count_exceeds_threshold', 'send_data_to_submission']

            if is_email_present():
                '''if email is present send_data_to_submission will not be the upstream task of end task,
                   at that time it will be notify_submission_failure
                '''
                del expected_upstream_task[2]
                expected_upstream_task.append("notify_submission_failure")

            upstream_task_ids=sorted(upstream_task_ids)
            expected_upstream_task=sorted(expected_upstream_task)
            msg = f'Upstream tasks for task \'end\' are not same as expected in DAG with id \'{dag_id}\''
            assert upstream_task_ids == expected_upstream_task ,msg

            downstream_task_ids = list(map(lambda task: task.task_id, end_task.downstream_list))
            expected_downstream_task=[]
            msg = f'DownStream tasks for task \'end\' are not same as expected in DAG with id \'{dag_id}\''
            assert downstream_task_ids == expected_downstream_task ,msg
