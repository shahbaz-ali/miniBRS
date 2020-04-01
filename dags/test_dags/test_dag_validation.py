import unittest
from airflow.models import DagBag

class TestDagValidation(unittest.TestCase):

    def setUp(self):
        self.dagbag = DagBag(dag_folder='/home/muhammad/AF_assingments/mini-brs/dags/generated')

    #OK
    def test_contain_cycles(self):
        id='incident'
        dag = self.dagbag.get_dag(id)
        result=dag.test_cycle() #resturn false if cycles are not present
        msg = f'Alert - The DAG with id {id} contain  cycle/cycles'
        self.assertFalse(result,msg)


    #OK
    def test_import_dags(self):
        self.assertFalse(
            len(self.dagbag.import_errors),
            'DAG import failures. Errors: {}'.format(
                self.dagbag.import_errors
            )
        )


    #OK
    def test_alert_email_present(self):

        for dag_id, dag in self.dagbag.dags.items():
            emails = dag.default_args.get('email', [])
            msg = 'Alert email not set for DAG {id}'.format(id=dag_id)
            self.assertIn('majid.kundroo@gmial.com', emails, msg)


     #OK
    def test_is_owner_present(self):
           for dag_id, dag in self.dagbag.dags.items():
               owner = dag.default_args.get('owner', "")
               msg = 'Alert - \'owner\' not set for DAG {id}'.format(id=dag_id)
               self.assertEqual("BRS",owner,msg)

    #OK
    def test_is_schedule_interval_present(self):
           for dag_id, dag in self.dagbag.dags.items():
               schedule_interval = dag.schedule_interval
               msg = 'Alert - \'schedule_interval\' not set for DAG {id}'.format(id=dag_id)
               self.assertGreater(len(schedule_interval),0,msg)

    #OK
    def test_is_DAGid_present(self):
           for dag_id, dag in self.dagbag.dags.items():
               msg = 'Alert - \'DAG id\' not set for one of DAG in DAG folder'
               self.assertGreater(len(dag_id),0,msg)

    # OK
    def test_is_start_date_present(self):
           for dag_id, dag in self.dagbag.dags.items():
               start_date = dag.default_args.get('start_date', "")
               msg = 'Alert - \'start_date\' not set for DAG {id}'.format(id=dag_id)
               self.assertGreater(len(dag_id),0,msg)

    #OK
    def test_get_existing_dag(self):
        """
        Test that we're able to parse some DAGs from generated folder and retrieve them
        """
        some_expected_dag_ids = ["incident"] # ["incident", "problem"]

        for dag_id in some_expected_dag_ids:
            dag = self.dagbag.get_dag(dag_id)

            self.assertIsNotNone(dag)
            self.assertEqual(dag_id, dag.dag_id)

    #OK
    def test_get_non_existing_dag(self):
        """
        test that retrieving a non existing dag id returns None without crashing
        """

        non_existing_dag_id = "non_existing_dag_id"
        dag=self.dagbag.get_dag(non_existing_dag_id) #must return none , because the "non_existing_dag_id"
                                                    # is the ID of ant DAG
        self.assertIsNone(dag)

    #OK
    def test_dont_load_example(self):
        """
        test that the example are not loaded
        """
        self.dagbag = DagBag(dag_folder='/home/muhammad/AF_assingments/mini-brs/dags/generated' , include_examples=False)
        size=self.dagbag.size()
        print(f"SIZE {size}")
        self.assertEqual(size, 1)


if __name__ == "__main__":
    unittest.main()