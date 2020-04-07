import pytest
from plugins.mbrs.utils.exceptions import InvalidArguments
from plugins.mbrs.utils.servicenow_client import ServiceNowClient
from plugins.mbrs.utils.servicenow_client import ServiceNowException

class TestServiceClientNow():
    sample_args = {
        'host': 'https://dev70631.service-now.com',
        'login': 'admin',
        'password': None,
        'client_id': None,
        'client_secret': None,
        'token': None,
        'refresh_token': None
    }

    #OK Py
    @pytest.mark.case1
    def test_object_creation_case1(self):
        # without  parameters

       with pytest.raises(InvalidArguments):
           ServiceNowClient()

    #OK Py
    @pytest.mark.case2
    def test_object_creation_case2(self):

        pytest.raises(InvalidArguments, ServiceNowClient,
                          login=self.sample_args.get('login'),
                          password=self.sample_args.get('password'),
                          )

    #OK Py
    @pytest.mark.case3
    def test_object_creation_case3(self):

       pytest.raises(InvalidArguments, ServiceNowClient,
                          host=self.sample_args.get('host'),
                          password=self.sample_args.get('password'),
                          )

    #OK Py
    @pytest.mark.case4
    def test_object_creation_case4(self):

        pytest.raises(ServiceNowException, ServiceNowClient,
                          host=self.sample_args.get('host'),
                          login=self.sample_args.get('login'),
                          )

    #OK Py
    @pytest.mark.case5
    def test_object_creation_case5(self):

        pytest.raises(ServiceNowException, ServiceNowClient,
                host=self.sample_args.get('host'),
                login=self.sample_args.get('login'),
                password=self.sample_args.get('password')
            )

    #OK
    @pytest.mark.case6
    def test_object_creation_case6(self):
        pytest.raises(InvalidArguments, ServiceNowClient,
                          host="",
                          login="",
                          password=""
                          )

    #OK
    @pytest.mark.case7
    def test_object_creation_case7(self):
        pytest.raises(InvalidArguments, ServiceNowClient,
                          host="",
                          login="",
                          password="*******"
                          )




