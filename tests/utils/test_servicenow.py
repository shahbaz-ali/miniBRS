import unittest
from datetime import  datetime
from plugins.mbrs.utils.servicenow import fetch_servicenow_record_count,on_failure_email,on_failure_context,clean_up
from plugins.mbrs.utils.exceptions import ConfigVariableNotFoundException, ServiceNowConnectionNotFoundException, \
    InvalidArguments


class TestServiceNow(unittest.TestCase):

    #OK
    def test_fetch_servicenow_record_count(self):

        with self.assertRaises(InvalidArguments):
            fetch_servicenow_record_count("  ", datetime.now())

        with self.assertRaises(InvalidArguments):
            fetch_servicenow_record_count(None, datetime.now())


        with self.assertRaises(InvalidArguments):
            fetch_servicenow_record_count(None, None)

    #OK
    def test_on_failure_email(self):

      with self.assertRaises(InvalidArguments):
          on_failure_email("  ", "", "")

      with self.assertRaises(InvalidArguments):
           on_failure_email("incident", "any_tag_id","")

    #OK
    def test_on_failure_context(self):

        with self.assertRaises(InvalidArguments):
            on_failure_context("", "", "", "", "")

        with self.assertRaises(InvalidArguments):
            on_failure_context("incident", "", "", "", "")

    #OK
    def test_clean_up(self):

        with self.assertRaises(InvalidArguments):
            clean_up("incident", "", "")

if __name__ == '__main__':
    unittest.main()
