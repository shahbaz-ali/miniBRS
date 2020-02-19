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

class S3ConnectionNotFoundException(AirflowException):
    '''
    @:exception: SFTPConnectionNotFoundException, raised if no connection
    with connection id 'sftp_global' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 's3_global' defined"

    def __str__(self):
        if self.message:
            return "S3ConnectionNotFoundException, {}".format(self.message)
        else:
            return "S3ConnectionNotFoundException has been raised"



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


class StorageTypeNotFoundException(AirflowException):
    '''
    @:exception: StorageTypeNotFoundException, raised if no variable
    storage_type is defined in 'config' variable

    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No Storage Type defined in config"

    def __str__(self):
        if self.message:
            return "StorageTypeNotFoundException, {}".format(self.message)
        else:
            return "StorageTypeNotFoundException has been raised"

class InvalidStorageTypeException(AirflowException):
    '''
    @:exception: Invalid Storage Type Exception, raised if
    storage_type defined in 'config' variable is not supported

    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "Invalid Storage Type defined in config"

    def __str__(self):
        if self.message:
            return "InvalidStorageTypeException, {}".format(self.message)
        else:
            return "InvalidStorageTypeException has been raised"



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


