#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import DropboxConnectionNotFoundException
from airflow.hooks.base_hook import BaseHook
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.exceptions import AirflowException
from airflow import configuration
from datetime import datetime, timedelta
import dropbox,os
from dropbox import files,exceptions

class ServiceNowToDropboxTransferOperator(ServiceNowToGenericTransferOperator):

    def is_storage_available(self, access_token):
        dbx = dropbox.Dropbox(access_token)
        try:
            curr_user = dbx.users_get_current_account()
            LoggingMixin().log.warning("CUrrent dropbox user :" + str(curr_user))

        except (exceptions.AuthError) as e:
            LoggingMixin().log.warning("Authentication Error : invalid dropbox access_token")
            return False
        except Exception as e:
            LoggingMixin().log.error("ServiceNow2DBXTransferError : error in dropbox connection")
            return False

        return True

    def _upload(self,context):

        # dropbox Connection details
        try:
            credentials_dropbox = BaseHook.get_connection(self.storage_conn_id)
            self.dropbox_access_token = credentials_dropbox.password
        except AirflowException as e:
            raise DropboxConnectionNotFoundException

        if self.is_storage_available(self.dropbox_access_token):
            try:
                LoggingMixin().log.info("Dropbox Storage avalaible")
                l_file_path = self.file_name.replace('.csv', '.json')
                file_name = l_file_path[l_file_path.rfind('/') + 1:]


                dt_current = datetime.strptime(self.execution_date[:19], "%Y-%m-%dT%H:%M:%S")

                exec_hour = str(dt_current.hour)
                exec_minute = str(dt_current.minute)
                exec_second = str(dt_current.second)

                if exec_hour == '0' and exec_minute == '0' and exec_second == '0':
                    dt_current = dt_current - timedelta(days=1)
                    r_file_path = '{}/{}/{}/{}/{}'.format(
                        '/mbrs',
                        'Servicenow',
                        self.table,
                        '{}-{}-{}'.format(
                            dt_current.year,
                            dt_current.month,
                            dt_current.day
                        ),
                        file_name)
                else:
                    r_file_path = '{}/{}/{}/{}/{}'.format(
                        '/mbrs',
                        'Servicenow',
                        self.table,
                        '{}-{}-{}'.format(
                            dt_current.year,
                            dt_current.month,
                            dt_current.day
                        ),
                        file_name)


                LoggingMixin().log.info("Running dropbox upload process...")
                try:
                    file_size = os.path.getsize(l_file_path)
                    CHUNK_SIZE = 4 * 1024 * 1024
                    dbx = dropbox.Dropbox(self.dropbox_access_token, timeout=600)
                    if file_size <= CHUNK_SIZE:
                        with open(l_file_path, 'rb') as f:
                            dbx.files_upload(f.read(), r_file_path, mode=dropbox.files.WriteMode.overwrite)
                            f.close()
                            return True
                    else:
                        with open(l_file_path, 'rb') as f:
                            upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                            cursor = dropbox.files.UploadSessionCursor(
                                session_id=upload_session_start_result.session_id,
                                offset=f.tell())
                            commit = dropbox.files.CommitInfo(path=r_file_path)
                            while f.tell() < file_size:
                                if (file_size - f.tell()) <= CHUNK_SIZE:
                                    print(dbx.files_upload_session_finish(f.read(CHUNK_SIZE),cursor,commit))
                                else:
                                    dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE),cursor)
                                    cursor.offset = f.tell()

                            f.close()
                            return True
                except Exception as e:
                    LoggingMixin().log.error("ServiceNow2DropBoxTransOperator : exception in dropbox upload for token : {} {}".format(
                                self.dropbox_access_token, e))
                    return False
            except Exception as e:
                print(e)
        else:
            LoggingMixin().log.info("Dropbox Storage not avalaible")
            return False



