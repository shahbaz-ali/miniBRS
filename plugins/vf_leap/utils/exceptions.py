#   vf_leap
#   Copyright (c)Cloud Innovation Partners 2020.
#   Author : Shahbaz Ali

from airflow.exceptions import AirflowException

class ServiceNowConnectionNotFoundException(AirflowException):

    '''
    @:exception: ServiceNowConnectionNotFoundException, raised if no connection
    with connection id 'snow_id' is found in the meta-database
    '''

    def __init__(self,*args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'snow_id' defined"

    def __str__(self):
        if self.message:
            return "ServiceNowConnectionNotFoundException, {}".format(self.message)
        else:
            return "ServiceNowConnectionNotFoundException has been raised"


class SFTPConnectionNotFoundException(AirflowException):
    '''
    @:exception: SFTPConnectionNotFoundException, raised if no connection
    with connection id 'sftp_global' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'sftp_global' defined"

    def __str__(self):
        if self.message:
            return "SFTPConnectionNotFoundException, {}".format(self.message)
        else:
            return "SFTPConnectionNotFoundException has been raised"


class ConfigVariableNotFoundException(AirflowException):
    '''
    @:exception: ConfigVariableNotFoundException, raised if no variable
    with key 'config' is found in the meta-database

    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No variable with key 'config' defined"

    def __str__(self):
        if self.message:
            return "ConfigVariableNotFoundException, {}".format(self.message)
        else:
            return "ConfigVariableNotFoundException has been raised"


class AirflowAPICredentialsNotFoundException(AirflowException):
    '''
    @:exception: AirflowAPICredentialsNotFoundException, raised if no connection
    with connection id 'rest' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'rest' defined"

    def __str__(self):
        if self.message:
            return "AirflowAPICredentialsNotFoundException, {}".format(self.message)
        else:
            return "AirflowAPICredentialsNotFoundException has been raised"