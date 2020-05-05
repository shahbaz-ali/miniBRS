"""
#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com
"""
import itertools
import xml.etree.ElementTree as ET
import pymssql as ms
from airflow import LoggingMixin
from airflow import AirflowException
from airflow.hooks.base_hook import BaseHook
from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator \
    import ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import MSSQLConnectionNotFoundException

count = 0


class ServiceNowToMSSQLTransferOperator(ServiceNowToGenericTransferOperator):
    """
    ServiceNowToMSSQLTransferOperator transfers the data from ServiceNow to Mssql.
    It parses the xml data of ServiceNow with the help of generators in python, and creates
    an object for each parsed data and stores it into MsSql database.
    """

    def _upload(self, context):
        """
        This method makes sure that the MsSql credentials are available, once they are available,
        we create a connection with the MsSql database with the help of these credentials.
        """
        try:
            credentials_mssql = BaseHook.get_connection(self.storage_conn_id)
            login = credentials_mssql.login
            password = credentials_mssql.password
            host = credentials_mssql.host
            database_name = credentials_mssql.schema
            port = credentials_mssql.port

            if not port:  # If port is empty,set default port number
                port = 1433
            LoggingMixin().log.warning(f'PORT NUMBER : {port}')
        except AirflowException as e:
            raise MSSQLConnectionNotFoundException()

        l_file_path = self.file_name
        LoggingMixin().log.warning(f'FILE PATH {l_file_path}')
        file_name = l_file_path[l_file_path.rfind('/') + 1:]
        table_name = self.table

        # get the col labels of table
        column_labels = Parser.get_col_lables(self._get_table_schema())

        # parse the file
        n_objects = Parser.get_n_objects(l_file_path)

        # store the data in the database
        storage = Storage(login, password, host, database_name, table_name, port)
        intial_record = next(n_objects)
        cols_keys = list(intial_record.keys())
        values_for_size = list(intial_record.values())
        storage.create_table(column_labels, values_for_size, cols_keys)
        storage.insert_data(n_objects, intial_record)


class Parser():
    """
    This class is actually responsible for parsing the xml data with the help of generators,
    and creates an object for each parsed data
    """

    global tree, markers, row_object, col_labels

    markers = []
    row_object = {}
    col_labels = []

    @staticmethod
    def get_col_lables(schema_generator):
        for obj in schema_generator:
            name = obj['name']
            name = name + "_" if name == 'order' else name  # marker for order is order_
            col_labels.append(name)
            if obj['reference'] is not None:
                markers.append(name)
        return col_labels

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
                        row_object[tag] = None  # pylint: disable=undefined-variable
                    else:
                        value_text = value.text
                        # sometimes the text will be none
                        row_object[tag] = "'" + value_text + "'" if value_text is not None else None

                elif tag not in ('link', 'value'):
                    row_object[tag] = "'" + str(
                        text).strip() + "'" if text is not None else None  # the text of some tags are none for example  <hold_reason />, <approval_history /> e.tc.

            elif event == 'end':
                if elem.tag == 'result':
                    yield row_object  # pylint: disable=undefined-variable
                    elem.clear()  # without this the memory usage goes very high


def get_query_with_col_size(column_names, values_for_size, cols_keys):
    """This method returns a query with column size """
    sub_query = ''
    i = 0
    for col in column_names:

        if col in cols_keys:
            value = values_for_size[i]
            data_type_size = len(value) if value is not None else 40
            data_type_size= 12 if data_type_size <=3 else data_type_size
            #print(col + "---" + str(value) + "---" + str(data_type_size))
            sub_query += col + " CHAR({}), ".format(data_type_size)
            i += 1
        else:
            print(col)
            sub_query += col + " CHAR(20), "

    return sub_query[:-2]


class Storage():
    """
    This class takes the MsSql credentials and creates a connection with MsSql database
    """

    def __init__(self, login, password, host, database_name, table_name, port):  # pylint: disable=too-many-arguments
        self.login = login
        self.password = password
        self.host = host
        self.database_name = database_name
        self.table_name = table_name
        self.port = port

    def create_table(self, column_names, values_for_size, cols_keys):
        """
        This method creates the table in the database(database name is specified in the parameter
        self.database_name )
        """

        conn = ms.connect(host=self.host, user=self.login, password=self.password,
                          port=self.port, database=self.database_name)
        cursor = conn.cursor()
        sub_query = get_query_with_col_size(column_names, values_for_size, cols_keys)
        check_if_table_exists = "if not exists (select * from sysobjects where name='{}')".format(self.table_name)
        sql = check_if_table_exists + ' CREATE TABLE {} ({});'.format(self.table_name, sub_query)
        print(sql)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def insert_data(self, n_objects, intial_record):
        """ This method inserts the parsed data(n_objects) in the MsSql database"""
        lst = []
        step = 100
        conn = ms.connect(server=self.host, user=self.login, password=self.password, database=self.database_name)
        cursor = conn.cursor()

        column_names = list(intial_record.keys())
        placeholders = ''.join("%s," * len(column_names))
        placeholders = placeholders.strip(',')
        column_names = ",".join(column_names)

        sql = "INSERT INTO {} ({}) VALUES ({})".format(self.table_name, column_names, placeholders)
        # insert intial_record first
        cursor.execute(sql, tuple(intial_record.values()))
        conn.commit()

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
