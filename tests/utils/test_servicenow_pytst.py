import pytest
from datetime import  datetime
from plugins.mbrs.utils.servicenow import fetch_servicenow_record_count,on_failure_email,on_failure_context,clean_up
from plugins.mbrs.utils.exceptions import ConfigVariableNotFoundException, ServiceNowConnectionNotFoundException, \
     InvalidArguments

import sys
if not sys.warnoptions:
    import os, warnings
    warnings.simplefilter("ignore") # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "ignore" # Also affect subprocesses


class TestServiceNow():

    #OK Py
    @pytest.mark.fetch_count
    def test_fetch_servicenow_record_count(self):

        with pytest.raises(InvalidArguments):
            fetch_servicenow_record_count("  ", datetime.now())

        with pytest.raises(InvalidArguments):
            fetch_servicenow_record_count(None, datetime.now())


        with pytest.raises(InvalidArguments):
            fetch_servicenow_record_count(None, None)

    #OK Py
    @pytest.mark.email_fail
    def test_on_failure_email(self):

      with pytest.raises(InvalidArguments):
          on_failure_email("  ", "", "")

      with pytest.raises(InvalidArguments):
           on_failure_email("incident", "any_tag_id","")

    #OK Py
    @pytest.mark.context_fail
    def test_on_failure_context(self):

        with pytest.raises(InvalidArguments):
            on_failure_context("", "", "", "", "")

        with pytest.raises(InvalidArguments):
            on_failure_context("incident", "", "", "", "")

    #OK Py
    @pytest.mark.clean
    def test_clean_up(self):

        with pytest.raises(InvalidArguments):
            clean_up("incident", "", "")
