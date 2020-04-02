import unittest
from datetime import  datetime
from plugins.mbrs.utils.servicenow import fetch_servicenow_record_count,on_failure_email,on_failure_context,clean_up
from plugins.mbrs.utils.exceptions import InvalidArguments, ConfigVariableNotFoundException,ServiceNowConnectionNotFoundException

class TestServiceNow(unittest.TestCase):

    def test_fetch_servicenow_record_count(self):

        with self.assertRaises(InvalidArguments):
            fetch_servicenow_record_count("  ", datetime.now())

        with self.assertRaises(InvalidArguments):
            fetch_servicenow_record_count(None, datetime.now())


        with self.assertRaises(InvalidArguments):
            fetch_servicenow_record_count(None, None)

        with self.assertRaises(KeyError):
            fetch_servicenow_record_count("incident", datetime.now())

        #keep the below cases separate, it has to be implements in integration phase
        # with self.assertRaises(ConfigVariableNotFoundException):
        #     fetch_servicenow_record_count("incident", datetime.now())

        # with self.assertRaises(ServiceNowConnectionNotFoundException):
        #     fetch_servicenow_record_count("incident", datetime.now())
        #
        # self.assertIsInstance(fetch_servicenow_record_count("incident", datetime.now()), str, msg=None)


    #
    #def test_on_failure_email(self):
    #
    #   with self.assertRaises(InvalidArguments):
    #       on_failure_email("", "", "")


    #    with self.assertRaises(InvalidArguments):
    #        on_failure_email("incident", "any_tag_id","")
    #
    #
    # def test_on_failure_context(self):
    #
    #     with self.assertRaises(InvalidArguments):
    #         on_failure_context("", "", "", "", "")
    #
    #     with self.assertRaises(InvalidArguments):
    #         on_failure_context("incident", "", "", "", "")
    #
    #
    # def test_clean_up(self):
    #
    #     with self.assertRaises(InvalidArguments):
    #         clean_up("incident", "", "")

if __name__ == '__main__':
    unittest.main()
