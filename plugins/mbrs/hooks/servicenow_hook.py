#  mbrs
#  Copyright (c)Cloud Innovation Partners 2020.
#  http://www.cloudinp.com

from airflow.hooks.base_hook import BaseHook
from airflow.exceptions import AirflowException
from airflow.models import Connection
from plugins.mbrs.utils.servicenow_client import ServiceNowClient

from airflow.utils.log.logging_mixin import LoggingMixin

class ServiceNowHook(BaseHook):

    """
    Interact with ServiceNow, using snowclient library.
    """
    AUTH_TYPE_BASIC = 0
    AUTH_TYPE_BEARER = 1

    def __init__(self,
                 auth_type=AUTH_TYPE_BASIC,
                 token=None,
                 login=None,
                 password=None,
                 host=None,
                 snow_conn_id=None):
        """
        Takes ServiceNow login, password and host directly and connection that is registered
        in connections model of airflow.

        Can be used for both types of authentication. we can supply the hook login name password
        and host for autheticating explicitly or it can take access_token if OAUTH is used.

        If both supplied, (username, password along with host) and (snow_conn_id) username password and host
        explicitly given will be used.

        :param auth_type: Authentication Type
        :param token: ServiceNow access_token
        :param login: ServiceNow username
        :param password: ServiceNow password
        :param host: ServiceNow instance url
        :param auth_type: int
        :type token: str
        :type login: str
        :type password: str
        :type host: str
        :param snow_conn_id: connection that has ServiceNow username, password and host field
        :type snow_conn_id: str
        """
        self.auth_type = auth_type
        self.snow_cred = self.__get_snow_cred(token, login, password, host, snow_conn_id)



    def __get_snow_cred(self,token, login, password, host, snow_conn_id):

        if self.auth_type == 1:
            if token is not None and host is not None:
                return Connection(
                    host=host,
                    password=token
                )
            elif token is None and host is not None:
                return Connection(
                    host=host
                )
            else:
                raise AirflowException("ServiceNowHook host not defined")
        elif self.auth_type == 0:
            if login is not None and password is not None and host is not None:

                return Connection(
                    host=host,
                    login=login,
                    password=password
                )

            elif snow_conn_id is not None:
                conn = self.get_connection(snow_conn_id)

                if not getattr(conn, 'password', None):
                    raise AirflowException('Missing password in ServiceNow connection')
                elif not getattr(conn,'host',None):
                    raise AirflowException('Missing host in ServiceNow Connection')
                elif not getattr(conn,'login',None):
                    raise AirflowException('Missing login name in ServiceNow Connection')
                else:
                    return conn
            else:
                raise AirflowException('Cannot access ServiceNow: '
                                       'No valid ServiceNow credentials nor snow_conn_id supplied.')

    def fetchAccessToken(self,
                         client_id=None,
                         client_secret=None,
                         login=None,
                         password=None,
                         refresh_token=None,
                         ):

        sc = ServiceNowClient(
            auth_type=1,
            host=self.snow_cred.host,
        )

        self.snow_cred.password = sc.fetchAccessToken(
            client_id=client_id,
            client_secret=client_secret,
            login=login,
            password=password,
            refresh_token=refresh_token
        )

        log = LoggingMixin().log
        log.info("Using connection to fetch access_token : %s", self.snow_cred.debug_info())

        return self.snow_cred.password

    def get_table_schema(self, table_name):
        """
        This method is used to get the schema of the table
        :param table_name: service now table name
        :return: Generator Object
        """

        client = ServiceNowClient(
                auth_type=0,
                host=self.snow_cred.host,
                login=self.snow_cred.login,
                password=self.snow_cred.password
            )

        return client.table_schema(table_name)

    def api_call(self, method='GET',route=None,query_params=None,accept=None):

        if route is None:
            raise AirflowException('provide valid value to argument route ')
        if not isinstance(query_params,dict):
            raise TypeError('query_param must be of type dict')
        if method not in ['GET','POST']:
            raise AirflowException('Method not implemented')

        if accept is not None :
            if (not str(accept).__eq__("application/json")) or (str(accept).__eq__('application/xml')):
                raise AirflowException("ServiceNowHook : accept can have only two value application\\json or application\\xml")


        #BASIC Authentication
        if self.auth_type == 0:
            sc = ServiceNowClient(
                auth_type=0,
                host=self.snow_cred.host,
                login=self.snow_cred.login,
                password=self.snow_cred.password
            )
            log = LoggingMixin().log
            log.info("Using basic connection to: %s", self.snow_cred.debug_info())

            rc = sc.api_call(method=method, route=route, query_params=query_params,accept=accept)
            return rc

        #BEARER Authentication
        elif self.auth_type == 1:
            sc = ServiceNowClient(
                auth_type=1,
                host=self.snow_cred.host,
                token=self.snow_cred.password
            )

            log = LoggingMixin().log
            log.info("Using oauth connection to: %s", self.snow_cred.debug_info())

            rc = sc.api_call(method=method,route=route, query_params=query_params,accept=accept)
            return rc