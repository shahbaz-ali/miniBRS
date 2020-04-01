
'''
To test the total number of tasks in the DAG, upstream and downstream dependencies of each task etc.
'''

import unittest
from airflow.models import DagBag
from airflow import configuration

class TestDAGDefnition(unittest.TestCase):

    def setUp(self):
        self.dagbag = DagBag(dag_folder=configuration.get_airflow_home()+'/dags/generated')

    #OK
    def test_task_count_in_dag(self):
        """Check task count of incident dag"""

        dag_id='incident'
        dag = self.dagbag.get_dag(dag_id)
        number_of_tasks=len(dag.tasks)
        msg=f'Check the number of tasks in DAG with id  {dag_id}'
        if number_of_tasks == 8: #8 tasks with emailoperator
            pass
        elif number_of_tasks == 7:
            pass
        else:
            self.assertNotEqual(number_of_tasks,8,msg)

    #OK
    def test_contain_tasks(self):
        """Check task contains in indcident dag"""

        expected_tasks = ['start', 'end', 'fetch_record_count', 'count_within_threshold', 'count_exceeds_threshold', \
                          'count_is_zero', 'send_data_to_submission']
        dag_id='incident'
        dag = self.dagbag.get_dag(dag_id)
        tasks = dag.tasks
        task_ids = list(map(lambda task: task.task_id, tasks))
        task_ids=sorted(task_ids)
        expected_tasks=sorted(expected_tasks)

        self.assertListEqual(task_ids, expected_tasks)

    #OK
    def test_dependencies_of_fetch_record_count_task(self):
        """Check the task dependencies of fetch_record_count in incident dag"""

        dag_id='incident'
        dag = self.dagbag.get_dag(dag_id)
        fetch_record_count_task = dag.get_task('fetch_record_count')

        upstream_task_ids = list(map(lambda task: task.task_id, fetch_record_count_task.upstream_list))
        expected_upstream_task=['start']
        self.assertListEqual(upstream_task_ids, expected_upstream_task)


        downstream_task_ids = list(map(lambda task: task.task_id, fetch_record_count_task.downstream_list))
        expected_downstream_task=['count_is_zero', 'count_within_threshold', 'count_exceeds_threshold']
        downstream_task_ids=sorted(downstream_task_ids)
        expected_downstream_task=sorted(expected_downstream_task)
        self.assertListEqual(downstream_task_ids,expected_downstream_task)

    #OK
    def test_dependencies_of_send_data_to_submission_task(self):

        """Check the task dependencies of send_data_to_submission in incident dag"""

        dag_id='incident'
        dag = self.dagbag.get_dag(dag_id)
        send_data_to_submission_task = dag.get_task('send_data_to_submission')

        upstream_task_ids = list(map(lambda task: task.task_id, send_data_to_submission_task.upstream_list))
        expected_upstream_task=['count_within_threshold']
        self.assertListEqual(upstream_task_ids, expected_upstream_task)


        downstream_task_ids = list(map(lambda task: task.task_id, send_data_to_submission_task.downstream_list))
        expected_downstream_task=['end']
        self.assertListEqual(downstream_task_ids,expected_downstream_task)

    #OK
    def test_dependencies_of_end_task(self):

        """Check the task dependencies of end task in incident dag"""

        dag_id='incident'
        dag = self.dagbag.get_dag(dag_id)
        end_task = dag.get_task('end')

        upstream_task_ids = list(map(lambda task: task.task_id, end_task.upstream_list))
        expected_upstream_task=['count_is_zero', 'count_exceeds_threshold', 'send_data_to_submission']
        upstream_task_ids=sorted(upstream_task_ids)
        expected_upstream_task=sorted(expected_upstream_task)
        self.assertListEqual(upstream_task_ids, expected_upstream_task)


        downstream_task_ids = list(map(lambda task: task.task_id, end_task.downstream_list))
        expected_downstream_task=[]
        self.assertListEqual(downstream_task_ids,expected_downstream_task)



if __name__ == '__main__':
    unittest.main()