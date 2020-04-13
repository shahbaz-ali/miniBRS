
'''
 To test the validity of the DAG, checking typos and cyclicity.
'''
import pytest
from airflow.models import DagBag
from airflow import configuration
from tests.ignores_warning import IgnoreWarnings

IgnoreWarnings.ignore()

class TestDagValidation():

    @pytest.fixture
    def dagbagDags(self):
        dagbag = DagBag(dag_folder=configuration.get_airflow_home() + '/dags/generated', include_examples= False)
        return dagbag.dags

    @pytest.fixture
    def dagbag(self):
        dagbag = DagBag(dag_folder=configuration.get_airflow_home() + '/dags/generated', include_examples= False)
        return dagbag

    #OK Py
    @pytest.mark.cycles
    def test_contain_cycles(self,dagbagDags,dagbag):
        #id='incident'
        for dag_id, _ in dagbagDags.items():
            dag = dagbag.get_dag(dag_id)
            result=dag.test_cycle() #resturn false if cycles are not present
            msg = f'Alert - The DAG with id \'{dag_id}\' contain  cycle/cycles'
            assert result == False ,msg


    #OK Py
    @pytest.mark.import_dags
    def test_import_dags(self,dagbag):
        assert len(dagbag.import_errors) == False ,\
            'DAG import failures. Errors: {}'.format(self.dagbag.import_errors)


    #OK Py
    @pytest.mark.owner
    def test_is_owner_present(self,dagbagDags):
           for dag_id, dag in dagbagDags.items():
               owner = dag.default_args.get('owner', "")
               msg = 'Alert - \'owner\' not set for DAG \'{id}\''.format(id=dag_id)
               assert len(owner.strip())>0 ,msg

    #OK Py
    @pytest.mark.interval
    def test_is_schedule_interval_present(self,dagbagDags):
           for dag_id, dag in dagbagDags.items():
               schedule_interval = dag.schedule_interval
               msg = 'Alert - \'schedule_interval\' not set for DAG \'{id}\''.format(id=dag_id)
               assert len(schedule_interval.strip()) > 0, msg

    #OK Py
    @pytest.mark.dag_id
    def test_is_DAGid_present(self,dagbagDags):
           for dag_id, dag in dagbagDags.items():
               msg = 'Alert - \'DAG id\' not set for one of DAG in DAG folder'
               assert len(dag_id.strip()) > 0, msg


    # OK py
    @pytest.mark.start_date
    def test_is_start_date_present(self,dagbagDags):
           for dag_id, dag in dagbagDags.items():
               start_date = dag.default_args.get('start_date', "")
               msg = 'Alert - \'start_date\' not set for DAG {id}'.format(id=dag_id)
               assert len(str(start_date).strip()) > 0, msg

    #OK
    @pytest.mark.existing_dag
    def test_get_existing_dag(self,dagbagDags, dagbag):
        """
        Test that we're able to parse some DAGs from generated folder and retrieve them
        """
        some_expected_dag_ids = [dag_id for dag_id, _ in dagbagDags.items()] # ["incident", "problem"]

        for dag_id in some_expected_dag_ids:
            dag = dagbag.get_dag(dag_id)

            assert dag != None
            assert dag_id == dag.dag_id

    #OK Py
    @pytest.mark.non_existing_dag
    def test_get_non_existing_dag(self,dagbag):
        """
        test that retrieving a non existing dag id returns None without crashing
        """

        non_existing_dag_id = "non_existing_dag_id"
        dag=dagbag.get_dag(non_existing_dag_id)  #must return none , because the "non_existing_dag_id"
                                                    # is not the ID of any DAG
        assert dag == None

    #OK
    @pytest.mark.not_load
    def test_dont_load_example(self):
        """
        test that the example are not loaded
        """
        dagbag = DagBag(dag_folder=configuration.get_airflow_home() + '/dags/generated', include_examples=False)
        size=dagbag.size()
        print(f"SIZE {size}")
        assert size == 0

