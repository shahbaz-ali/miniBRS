"""
#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com
"""
import itertools
import xml.etree.ElementTree as ET
import MySQLdb as ms
from airflow import LoggingMixin

from airflow import AirflowException
from airflow.hooks.base_hook import BaseHook
from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import \
    ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import MYSQLConnectionNotFoundException

class ServiceNowToMYSQLTransferOperator(ServiceNowToGenericTransferOperator):
    """
         ServiceNowToMYSQLTransferOperator transfers the data from ServiceNow to Mysql.
         It parses the xml data of ServiceNow with the help of generators in python, and creates
         an object for each parsed data and stores it into MySql database.
      """
    def _upload(self, context):
        """
         This method makes sure that the MySql credentials are available, once they are available,
         we create a connection with the MySql database with the help of these credentials.
         """
        try:
            credentials_mysql = BaseHook.get_connection(self.storage_conn_id)
            login = credentials_mysql.login
            password = credentials_mysql.password
            host = credentials_mysql.host
            database_name = credentials_mysql.schema
            port = credentials_mysql.port

            if not port:  #If port is empty,set default port number
                port=3306
            LoggingMixin().log.warning(f'PORT NUMBER : {port}')

        except AirflowException:
            raise MYSQLConnectionNotFoundException()

        l_file_path = self.file_name
        LoggingMixin().log.warning(f'FILE PATH {l_file_path}')
        file_name = l_file_path[l_file_path.rfind('/') + 1:]
        table_name = file_name.split('_')[0]  #gets the table name from file name

        #parse the file
        n_objects = ParseFile.get_n_objects(l_file_path)

        #store the data in the database
        cols = list(next(n_objects).keys())
        storage = Storage(login, password, host, database_name, table_name, port)
        #storage.create_database()
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
        """ This methos pareses the xaml file with the help of iterpase() method """
        tree = ET.iterparse(file_path, events=('start', 'end'))
        for event, elem in tree:
            if event == 'start' and elem.tag != 'response' and elem.tag != 'result':
                tag = elem.tag
                text = elem.text

                if tag == 'order':  # order is a keyword in sql, shows syntax error in query
                    tag = tag + "_"

                # check for markers
                if tag in markers:  #pylint: disable=undefined-variable
                    link = elem.find('link')

                    # check link for none -- sometimes the link will be None
                    if link is None:
                        incident[tag] = '\'Not present\''  #pylint: disable=undefined-variable
                    else:
                        link_text = link.text
                        # sometimes the text will be none
                        incident[tag] = "'" + link_text + "'" if link_text is not None else "\'empty\'" #pylint: disable=undefined-variable

                elif tag not in ('link', 'value'):
                    incident[tag] = "'" + str(text).strip() + "'"  #pylint: disable=undefined-variable

            elif event == 'end':
                if elem.tag == 'result':
                    yield incident  #pylint: disable=undefined-variable
                    elem.clear()  # without this the memory usage goes very high


class Storage():
    """
    This class takes the MySql credentials and creates a connection with MySql database
    """
    def __init__(self, login, password, host, database_name, table_name,port):   # pylint: disable=too-many-arguments
        self.login = login
        self.password = password
        self.host = host
        self.database_name = database_name
        self.table_name = table_name
        self.port=port

    # def create_database(self):
    #     conn = ms.connect(host=self.host, user=self.login, password=self.password)
    #     cursor = conn.cursor()
    #     sql = 'CREATE DATABASE IF NOT EXISTS ' + self.database_name
    #     cursor.execute(sql)
    #     conn.commit()
    #     conn.close()

    def create_table(self, column_names):
        """
        This method creates the table in the database(database name is specified in the parameter
        self.database_name )
        """
        conn = ms.connect(host=self.host, user=self.login, password=self.password,
                          port=self.port, db=self.database_name)
        cursor = conn.cursor()
        column_names = ','.join("`" + col_name + "` varchar(100)" for col_name in column_names)
        sql = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(self.table_name, column_names)
        # print(sql)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def insert_data(self, n_objects, column_names):
        """ This method inserts the parsed data(n_objects) in the MySql database"""
        lst = []
        step = 100
        conn = ms.connect(host=self.host, user=self.login, password=self.password,
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
