import unittest

from plugins.mbrs.utils.exceptions import InvalidArguments
from plugins.mbrs.utils.servicenow_client import ServiceNowClient
from plugins.mbrs.utils.servicenow_client import ServiceNowException

class TestServiceClientNow(unittest.TestCase):
    sample_args = {
        'host': 'https://dev70631.service-now.com',
        'login': 'admin',
        'password': None,
        'client_id': None,
        'client_secret': None,
        'token': None,
        'refresh_token': None
    }

    #OK
    def test_object_creation_case1(self):
        # without  parameters

       with self.assertRaises(InvalidArguments):
           ServiceNowClient()

    #OK
    def test_object_creation_case2(self):

        self.assertRaises(InvalidArguments, ServiceNowClient,
                          login=self.sample_args.get('login'),
                          password=self.sample_args.get('password'),
                          )

    #OK
    def test_object_creation_case3(self):

        self.assertRaises(InvalidArguments, ServiceNowClient,
                          host=self.sample_args.get('host'),
                          password=self.sample_args.get('password'),
                          )

    #OK
    def test_object_creation_case4(self):

        self.assertRaises(ServiceNowException, ServiceNowClient,
                          host=self.sample_args.get('host'),
                          login=self.sample_args.get('login'),
                          )

    #OK
    def test_object_creation_case5(self):

        self.assertRaises(ServiceNowException, ServiceNowClient,
                host=self.sample_args.get('host'),
                login=self.sample_args.get('login'),
                password=self.sample_args.get('password')
            )

    #OK
    def test_object_creation_case6(self):
        self.assertRaises(InvalidArguments, ServiceNowClient,
                          host="",
                          login="",
                          password=""
                          )

    #OK
    def test_object_creation_case7(self):
        self.assertRaises(InvalidArguments, ServiceNowClient,
                          host="",
                          login="",
                          password="*******"
                          )


if __name__=='__main__':
    unittest.main()

