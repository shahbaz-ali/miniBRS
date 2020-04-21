#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

from airflow.exceptions import AirflowException

class ServiceNowConnectionNotFoundException(AirflowException):

    '''
    @:exception: ServiceNowConnectionNotFoundException, raised if no connection
    with connection id 'servicenow_default' is found in the meta-database
    '''

    def __init__(self,*args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'servicenow_default' defined"

    def __str__(self):
        if self.message:
            return "ServiceNowConnectionNotFoundException, {}".format(self.message)
        else:
            return "ServiceNowConnectionNotFoundException has been raised"


class SFTPConnectionNotFoundException(AirflowException):
    '''
    @:exception: SFTPConnectionNotFoundException, raised if no connection
    with connection id 'sftp_default' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'sftp_default' defined"

    def __str__(self):
        if self.message:
            return "SFTPConnectionNotFoundException, {}".format(self.message)
        else:
            return "SFTPConnectionNotFoundException has been raised"

class S3ConnectionNotFoundException(AirflowException):
    '''
    @:exception: S3ConnectionNotFoundException, raised if no connection
    with connection id 's3_default' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 's3_default' defined"

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


class DropboxConnectionNotFoundException(AirflowException):
    '''
    @:exception: DropboxConnectionNotFoundException, raised if no connection
    with connection id 'dropbox_default' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'dropbox_default' defined"

    def __str__(self):
        if self.message:
            return "DropboxConnectionNotFoundException, {}".format(self.message)
        else:
            return "DropboxConnectionNotFoundException has been raised"


class BadStartDatePreset(AirflowException):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "Unknown start_date preset value used in DAG"

    def __str__(self):
        if self.message:
            return "BadStartPreset, {}".format(self.message)
        else:
            return "BadStartPreset has been raised"



class InvalidArguments(AirflowException):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "Invalid Arguments"

    def __str__(self):
        if self.message:
            return "InvalidArguments, {}".format(self.message)
        else:
            return "InvalidArguments has been raised"

class PostgreSQLConnectionNotFoundException(AirflowException):
    '''
    @:exception: PostgreSQLConnectionNotFoundException, raised if no connection
    with connection id 'postgres_default' is found in the meta-database
    '''
    
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'postgres_default' defined"

    def __str__(self):
        if self.message:
            return "PostgreSQLConnectionNotFoundException, {}".format(self.message)
        else:
            return "PostgreSQLConnectionNotFoundException has been raised"
          
          
class MYSQLConnectionNotFoundException(AirflowException):
    '''
    @:exception: MYSQLConnectionNotFoundException, raised if no connection
    with connection id 'mysql_default' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'mysql_default' defined"

    def __str__(self):
        if self.message:
            return "MYSQLConnectionNotFoundException, {}".format(self.message)
        else:
            return "MYSQLConnectionNotFoundException has been raised"

class MSSQLConnectionNotFoundException(AirflowException):
    '''
    @:exception: MSSQLConnectionNotFoundException, raised if no connection
    with connection id 'mssql_default' is found in the meta-database
    '''

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "No connection with id 'mssql_default' defined"

    def __str__(self):
        if self.message:
            return "MSSQLConnectionNotFoundException, {}".format(self.message)
        else:
            return "MSSQLConnectionNotFoundException has been raised"
