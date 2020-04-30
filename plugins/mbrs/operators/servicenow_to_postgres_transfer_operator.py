"""
#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   hhtp://cloudinp.com
"""
import itertools
import xml.etree.ElementTree as ET
import psycopg2 as pg
from airflow import LoggingMixin
from airflow import AirflowException
from airflow.hooks.base_hook import BaseHook

from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import \
    ServiceNowToGenericTransferOperator

from plugins.mbrs.utils.exceptions import PostgreSQLConnectionNotFoundException


class ServiceNowToPostgresqlTransferOperator(ServiceNowToGenericTransferOperator):
    """
       ServiceNowToPostgresqlTransferOperator transfers the data from ServiceNow to Postgresql.
       It parses the xml data of ServiceNow with the help of generators in python, and creates
       an object for each parsed data and stores it into Postgresql database.
    """

    def _upload(self, context):
        """
        This method makes sure that the Postgres credentials are available, once they are available,
        we create a connection with the Postgresql database with the help of these credentials.
        """
        try:
            credentials_postgres = BaseHook.get_connection(self.storage_conn_id)
            login = credentials_postgres.login
            password = credentials_postgres.password
            host = credentials_postgres.host
            database_name = credentials_postgres.schema
            port = credentials_postgres.port

            if not port:  # If port is empty,set default port number
                port = 5432
            LoggingMixin().log.warning(f'PORT NUMBER : {port}')

        except AirflowException:
            raise PostgreSQLConnectionNotFoundException()

        l_file_path = self.file_name
        LoggingMixin().log.warning(f'FILE PATH {l_file_path}')
        file_name = l_file_path[l_file_path.rfind('/') + 1:]
        table_name = file_name.split('_')[0]  # gets the table name from file name

        # parse the file
        n_objects = ParseFile.get_n_objects(l_file_path)

        # store the data in the database
        cols = list(next(n_objects).keys())
        storage = Storage(login, password, host, database_name, table_name, port)
        storage.create_table(cols)
        storage.insert_data(n_objects, cols)


# pylint: disable=too-few-public-methods
class ParseFile():
    """
       This class is actually responsible for parsing the xml data with the help of generators,
       and creates an object for each parsed data
    """

    global tree, markers, incident

    markers = ['opened_by', 'sys_domain', 'caller_id', 'assignment_group']
    incident = {}

    @staticmethod
    def get_n_objects(file_path):
        """ This method pareses the xml file with the help of iterpase() method """
        tree = ET.iterparse(file_path, events=('start', 'end'))
        for event, elem in tree:
            if event == 'start' and elem.tag != 'response' and elem.tag != 'result':
                tag = elem.tag
                text = elem.text

                if tag == 'order':  # order is a keyword in sql, shows syntax error in query
                    tag = tag + "_"

                # check for markers
                if tag in markers:  # pylint: disable=undefined-variable
                    value = elem.find('value')

                    # check value for none -- sometimes the value will be None
                    if value is None:
                        incident[tag] = '\'Not present\''  # pylint: disable=undefined-variable
                    else:
                        value_text = value.text
                        # sometimes the text will be none
                        incident[
                            tag] = "'" + value_text + "'" if value_text is not None else "\'Not present\'"  # pylint: disable=undefined-variable

                elif tag not in ('link', 'value'):
                    incident[tag] = "'" + str(text).strip() + "'"  # pylint: disable=undefined-variable

            elif event == 'end':
                if elem.tag == 'result':
                    yield incident  # pylint: disable=undefined-variable
                    elem.clear()  # without this the memory usage goes very high


class Storage():
    """
    This class takes the Postgresql credentials and creates a connection with Postgresql database
    """

    def __init__(self, login, password, host, database_name, table_name, port):  # pylint: disable=too-many-arguments
        self.login = login
        self.password = password
        self.host = host
        self.database_name = database_name
        self.table_name = table_name
        self.port = port

    def create_table(self, column_names):
        """
        This method creates the table in the database(database name is specified in the parameter
        self.database_name )
        """
        conn = pg.connect(host=self.host, port=self.port, user=self.login, password=self.password,
                          database=self.database_name)
        cursor = conn.cursor()
        column_names = ','.join(col_name + " CHAR(100)" for col_name in column_names)
        sql = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(self.table_name, column_names)
        print(sql)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def insert_data(self, n_objects, column_names):
        """ This method inserts the parsed data(n_objects) in the Postgresql database"""
        lst = []
        step = 100
        conn = pg.connect(host=self.host, port=5432, user=self.login, password=self.password,
                          database=self.database_name)
        cursor = conn.cursor()

        placeholders = ''.join("%s," * len(column_names))
        placeholders = placeholders.strip(',')
        column_names = ",".join(column_names)

        sql = "INSERT INTO {} ({}) VALUES ({})".format(self.table_name, column_names, placeholders)
        # print(sql)

        while True:  # traverse to the end of the generator object
            itr = itertools.islice(n_objects, 0, step)
            for i in itr:
                lst.append(tuple(i.values()))
            # print(lst)
            if not lst:  # check for lst is empty, if empty that means end of generator is reached.
                break
            cursor.executemany(sql, lst)
            conn.commit()
            lst.clear()
        conn.close()
