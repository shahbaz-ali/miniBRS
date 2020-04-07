
'''
To test the total number of tasks in the DAG, upstream and downstream dependencies of each task etc.
'''

import unittest

from airflow.exceptions import AirflowConfigException
from airflow.models import DagBag
from airflow import configuration


def is_email_present():
        isPresent=False
        try:
            configuration.get('smtp', 'smtp_user')
            isPresent = True
        except AirflowConfigException as e:
            isPresent=False

        return isPresent

class TestDAGDefnition(unittest.TestCase):

    def setUp(self):
        self.dagbag = DagBag(dag_folder=configuration.get_airflow_home()+'/dags/generated')

    # #OK
    def test_task_count_in_dag(self):
        """Check task count of a dag"""

        for dag_id, dag in self.dagbag.dags.items():

            #dag_id='incident'
            dag = self.dagbag.get_dag(dag_id)
            number_of_tasks=len(dag.tasks)
            msg=f'Number of tasks are not same as expected in DAG with id  {dag_id}'

            if is_email_present():
                '''Total number of tasks in a dag will be 8'''
                self.assertEqual(number_of_tasks,8,msg)
            else:
                '''Without email operator total tasks will be 7'''
                self.assertEqual(number_of_tasks, 7, msg)

    #OK
    def test_is_email_task_present(self):
        isPresent=False
        for dag_id, dag in self.dagbag.dags.items():
            try:
                configuration.get('smtp', 'smtp_user')
                isPresent = True
            except AirflowConfigException as e:
                isPresent=False
                msg= f'Email operator is not present in the DAG with id {dag_id}'

            self.assertEquals(isPresent,False,msg)

    #OK
    def test_contain_tasks(self):
        """Check task contains in a dag"""

        expected_tasks = ['start', 'end', 'fetch_record_count', 'count_within_threshold', 'count_exceeds_threshold', \
                          'count_is_zero', 'send_data_to_submission']

        if is_email_present():
            expected_tasks.append("notify_submission_failure")
        for dag_id, dag in self.dagbag.dags.items():

           # dag_id='incident'
            dag = self.dagbag.get_dag(dag_id)
            tasks = dag.tasks
            task_ids = list(map(lambda task: task.task_id, tasks))
            task_ids=sorted(task_ids)
            expected_tasks=sorted(expected_tasks)
            msg=f'Tasks in DAG with id \'{dag_id}\' are not same as expected'
            self.assertListEqual(task_ids, expected_tasks,msg)

    #OK
    def test_dependencies_of_fetch_record_count_task(self):
        """Check the task dependencies of fetch_record_count in a dag"""

        for dag_id, dag in self.dagbag.dags.items():

            #dag_id='incident'
            dag = self.dagbag.get_dag(dag_id)
            fetch_record_count_task = dag.get_task('fetch_record_count')

            upstream_task_ids = list(map(lambda task: task.task_id, fetch_record_count_task.upstream_list))
            expected_upstream_task=['start']
            msg=f'Upstream tasks of fetch_record_count in a DAG with id \'{dag_id}\' are not same as expected'
            self.assertListEqual(upstream_task_ids, expected_upstream_task,msg)


            downstream_task_ids = list(map(lambda task: task.task_id, fetch_record_count_task.downstream_list))
            expected_downstream_task=['count_is_zero', 'count_within_threshold', 'count_exceeds_threshold']
            downstream_task_ids=sorted(downstream_task_ids)
            expected_downstream_task=sorted(expected_downstream_task)
            msg=f'DownStream tasks of fetch_record_count in a DAG with id \'{dag_id}\' are not same as expected'
            self.assertListEqual(downstream_task_ids,expected_downstream_task,msg)

    #OK
    def test_dependencies_of_send_data_to_submission_task(self):

        """Check the task dependencies of send_data_to_submission in incident dag"""
        for dag_id, dag in self.dagbag.dags.items():

           # dag_id='incident'
            dag = self.dagbag.get_dag(dag_id)
            send_data_to_submission_task = dag.get_task('send_data_to_submission')

            upstream_task_ids = list(map(lambda task: task.task_id, send_data_to_submission_task.upstream_list))
            expected_upstream_task=['count_within_threshold']
            msg=f'Upstream tasks for task \'send_data_to_submission\' are not same as expected in DAG with id \'{dag_id}\''
            self.assertListEqual(upstream_task_ids, expected_upstream_task,msg)


            downstream_task_ids = list(map(lambda task: task.task_id, send_data_to_submission_task.downstream_list))
            expected_downstream_task=['end']
            if is_email_present():
                '''if email is present the downstream task of send_data_to_submission will be
                   notify_submission_failure, not the end task
                '''
                del expected_downstream_task[0]
                expected_downstream_task.append("notify_submission_failure")
                expected_downstream_task=sorted(expected_downstream_task)
            self.assertListEqual(downstream_task_ids,expected_downstream_task)

    #OK
    def test_dependencies_of_end_task(self):

        """Check the task dependencies of end task in incident dag"""

        for dag_id, dag in self.dagbag.dags.items():
            #dag_id='incident'
            dag = self.dagbag.get_dag(dag_id)
            end_task = dag.get_task('end')

            upstream_task_ids = list(map(lambda task: task.task_id, end_task.upstream_list))
            expected_upstream_task=['count_is_zero', 'count_exceeds_threshold', 'send_data_to_submission']

            if is_email_present():
                '''if email is present send_data_to_submission will not be the upstream task of end task,
                   at that time it will be notify_submission_failure
                '''
                del expected_upstream_task[2]
                expected_upstream_task.append("notify_submission_failure")

            upst,ream_task_ids=sorted(upstream_task_ids)
            expected_upstream_task=sorted(expected_upstream_task)
            msg = f'Upstream tasks for task \'end\' are not same as expected in DAG with id \'{dag_id}\''
            self.assertListEqual(upstream_task_ids, expected_upstream_task,msg)


            downstream_task_ids = list(map(lambda task: task.task_id, end_task.downstream_list))
            expected_downstream_task=[]
            msg = f'DownStream tasks for task \'end\' are not same as expected in DAG with id \'{dag_id}\''
            self.assertListEqual(downstream_task_ids,expected_downstream_task,msg)



if __name__ == '__main__':
    unittest.main()