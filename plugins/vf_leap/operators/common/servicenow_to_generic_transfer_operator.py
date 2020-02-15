#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow.models.baseoperator import BaseOperator

class ServiceNowToGenericTransferOperator(BaseOperator):


    def _upload(self):

        """
        This method should be overridden by child class
        :return:
        :raises NotImplementedError

        """

        raise NotImplementedError


    def execute(self, context):

        #TODO implement Generic transfer logic
        pass