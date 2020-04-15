#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

from airflow import AirflowException
from airflow.hooks.base_hook import BaseHook
from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import MYSQLConnectionNotFoundException
import xml.etree.ElementTree as ET
import MySQLdb as ms
from airflow import LoggingMixin

count=0

class ServiceNowToMYSQLTransferOperator(ServiceNowToGenericTransferOperator):

    def _upload(self, context):

        try:
            credentials_mysql = BaseHook.get_connection(self.storage_conn_id)
            self.login = credentials_mysql.login
            self.password = credentials_mysql.password
            self.host = credentials_mysql.host
            self.database_name = credentials_mysql.schema
        except AirflowException as e:
            raise MYSQLConnectionNotFoundException()

        l_file_path = self.file_name
        LoggingMixin().log.warning(f'FILE PATH {l_file_path}')
        file_name = l_file_path[l_file_path.rfind('/') + 1:]
        table_name = file_name.split('_')[0]  #gets the table name from file name

        #parse the file
        n_objects = ParseFile.get_n_objects(l_file_path)

        #store the data in the database
        cols = list(next(n_objects).keys())
        storage = Storage(self.login, self.password, self.host, self.database_name, table_name)
        #storage.create_database()
        storage.create_table(cols)
        storage.insert_data(n_objects)


class ParseFile():
    global tree, markers, incident

    markers = ['opened_by', 'sys_domain', 'caller_id', 'assignment_group']
    incident = {}

    @staticmethod
    def get_n_objects(file_path):
        tree = ET.iterparse(file_path, events=('start', 'end'))
        for event, elem in tree:
            if event == 'start' and elem.tag != 'response' and elem.tag != 'result':
                tag = elem.tag
                text = elem.text

                if tag == 'order':  # order is a keyword in sql, shows syntax error in query
                    tag = tag + "_"

                # check for markers
                if tag in markers:
                    link = elem.find('link')

                    # check link for none -- sometimes the link will be None
                    if link == None:
                        incident[tag] = '\'Not present\''
                    else:
                        link_text = link.text
                        # sometimes the text will be none
                        incident[tag] = "'" + link_text + "'" if link_text != None else "\'empty\'"

                elif tag != 'link' and tag != 'value':
                    incident[tag] = "'" + str(text).strip() + "'"

            elif event == 'end':
                if elem.tag == 'result':
                    yield incident
                    elem.clear()  # without this the memory usage goes very high


class Storage():

    def __init__(self, login, password, host, database_name, table_name):
        self.login = login
        self.password = password
        self.host = host
        self.database_name = database_name
        self.table_name = table_name

    def create_database(self):
        conn = ms.connect(host=self.host, user=self.login, password=self.password)
        cursor = conn.cursor()
        sql = 'CREATE DATABASE IF NOT EXISTS ' + self.database_name
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def create_table(self, column_names):
        conn = ms.connect(host=self.host, user=self.login, password=self.password, db=self.database_name)
        cursor = conn.cursor()
        column_names = ','.join("`" + col_name + "` varchar(100)" for col_name in column_names)
        sql = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(self.table_name, column_names)
        # print(sql)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def insert_data(self, n_objects):
        count=0
        conn = ms.connect(host=self.host, user=self.login, password=self.password, db=self.database_name)
        cursor = conn.cursor()

        obj = next(n_objects)
        cols = ",".join(obj.keys())
        for object in n_objects:
            values = ",".join(object.values())
            sql = "INSERT INTO {} ({}) VALUES ({})".format(self.table_name, cols, values)
            cursor.execute(sql)
            conn.commit()
            count += 1
            LoggingMixin().log.warning(f'Inserting Record {count} ')
        conn.close()
