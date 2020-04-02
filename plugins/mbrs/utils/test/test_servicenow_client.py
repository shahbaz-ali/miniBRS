import unittest
from plugins.mbrs.utils.servicenow_client import ServiceNowClient
from plugins.mbrs.utils.exceptions import InvalidArguments
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

    # def setUp(self):
    #     self.service_now_client=ServiceNowClient()
    #
    # def tearDown(self):
    #     self.service_now_client=None

    def test_object_creation_case1(self):
        # without  parameters

       with self.assertRaises(InvalidArguments):
           ServiceNowClient()


    def test_object_creation_case2(self):

        self.assertRaises(InvalidArguments, ServiceNowClient,
                          login=self.sample_args.get('login'),
                          password=self.sample_args.get('password'),
                          )

    def test_object_creation_case3(self):

        self.assertRaises(InvalidArguments, ServiceNowClient,
                          host=self.sample_args.get('host'),
                          password=self.sample_args.get('password'),
                          )

    def test_object_creation_case4(self):

        self.assertRaises(InvalidArguments, ServiceNowClient,
                          host=self.sample_args.get('host'),
                          login=self.sample_args.get('login'),
                          )

    def test_object_creation_case5(self):

        self.assertRaises(InvalidArguments, ServiceNowClient,
                host=self.sample_args.get('host'),
                login=self.sample_args.get('login'),
                password=self.sample_args.get('password')
            )

    def test_object_creation_case6(self):
        self.assertRaises(InvalidArguments, ServiceNowClient,
                          host="",
                          login="",
                          password=""
                          )

    # def test_object_creation_case6(self):
    #
    #     try:
    #         ServiceNowClient(,,
    #             host=self.default_args.get('host'),
    #             login=self.default_args.get('login'),
    #             password=self.default_args.get('password'),
    #             auth_type=1,
    #             client_id=self.default_args.get('client_id'),
    #             client_secret=self.default_args.get('client_secret'),
    #             token=self.default_args.get('token'),
    #             refresh_token=self.default_args.get('refresh_token')
    #         )
    #     except ServiceNowException:
    #         self.fail("System Failure : ServiceNowClient Raised Exception")


    # def test_fetchAccessToken(self):
    #
    #     with self.assertRaises(InvalidArguments):
    #         self.service_now_client.fet

if __name__=='__main__':
    unittest.main()

