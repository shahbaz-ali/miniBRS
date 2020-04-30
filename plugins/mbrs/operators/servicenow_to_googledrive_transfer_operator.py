#   mbrs
#   Copyright (c)Cloud Innovation Partners 2020.
#   http://www.cloudinp.com

from airflow import AirflowException
from airflow.hooks.base_hook import BaseHook
from airflow.utils.decorators import apply_defaults
from airflow.utils.log.logging_mixin import LoggingMixin
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from oauth2client.client import GoogleCredentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from apiclient import errors
import socket, httplib2, oauth2client, json, traceback, pendulum

from plugins.mbrs.operators.common.servicenow_to_generic_transfer_operator import ServiceNowToGenericTransferOperator
from plugins.mbrs.utils.exceptions import GoogleDriveConnectionNotFoundException


def get_new_access_token(gdrv_client_id, gdrv_client_secret, refresh_token):
    try:
        cred = GoogleCredentials(
            None,
            gdrv_client_id,
            gdrv_client_secret,
            refresh_token,
            None,
            "https://accounts.google.com/o/oauth2/token",
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
        )

        http = cred.authorize(httplib2.Http())
        cred.refresh(http)

        access_token = json.loads(cred.to_json()).get("access_token")
        #self.gdrv_access_token_list.append(str(access_token))
        return  access_token
    except oauth2client.client.HttpAccessTokenRefreshError as e:

        LoggingMixin().log.warning("Authentication Error : invalid google_drive refresh_token")


class ServiceNowToGoogleDriveTransferOperator(ServiceNowToGenericTransferOperator):

    gdrv_token_uri = 'https://oauth2.googleapis.com/token'
    gdrv_access_token = None
    gdrv_credentials = None

    def _upload(self, context):
        LoggingMixin().log.info("Running google_drive upload process...")

        try:
            # Load Google Drive storage_credentials
            credentials_drive = BaseHook.get_connection(self.storage_conn_id)
            gdrv_client_id = credentials_drive.login
            gdrv_client_secret = credentials_drive.password
            refresh_token = json.loads(credentials_drive.get_extra())["refresh_token"]
        except AirflowException as e:
            raise GoogleDriveConnectionNotFoundException()

        access_token=get_new_access_token(gdrv_client_id, gdrv_client_secret, refresh_token)

        dt_current = datetime.strptime(self.execution_date[:19], "%Y-%m-%dT%H:%M:%S")
        self.l_file_path = self.file_name
        index = self.l_file_path.rfind('/')
        file_name = self.l_file_path[index + 1:]

        r_file_path = '{}/{}/{}/{}/{}'.format(
            'mbrs',
            'ServiceNow',
            self.table,
            '{}-{}-{}'.format(
                dt_current.year,
                dt_current.month,
                dt_current.day
            ),
            file_name)

        self.gdrv_credentials = Credentials(token=access_token, refresh_token=refresh_token)

        try:

                r_parent_file = None

                parts = str(r_file_path).split('/')

                for file in parts:

                    if file == '':
                        pass

                    elif file == 'mbrs':

                        if self.__is_folder_available(file):
                            pass

                        else:
                            LoggingMixin().log.warning(f"Creating {file} folder")
                            self.__create_folder(file)

                        r_parent_file = self.__get_folder_id(file)

                    elif str(file) == str(parts[len(parts) - 1]):

                        if self.__is_file_available(file):
                            LoggingMixin().log.warning("%s file already exists and will be rewritten ", file)
                            self.__delete_file(file)

                        file_metadata = {
                            'name': file,
                            'parents': [r_parent_file]
                        }

                        media = MediaFileUpload(self.l_file_path, mimetype='text/xml')
                        drive_service = build('drive', 'v3', credentials=self.gdrv_credentials, cache_discovery=False)

                        f = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                        LoggingMixin().log.info("file upload request/sucess id %s ", f.get('id'))

                    else:
                        if not self.__is_folder_available(file, r_parent_file):

                            self.__create_folder(
                                folder_name=file,
                                parent=r_parent_file
                            )

                            r_parent_file = self.__get_folder_id(file)

                        else:
                            r_parent_file = self.__get_folder_id(file)

                return True

        except Exception as e:

            LoggingMixin().log.error("Exception occured while uploading file")

    def __is_folder_available(self, folder_name, grdv_root='root'):

        '''
        checks whether folder specified by 'folder_name' is available in google drive as child folder under
        folder specified by 'gdrv_root'

        :param folder_name: folder name
        :param grdv_root: parent folder name
        :return: boolean
        '''

        # try:
        service = build('drive', 'v3', credentials=self.gdrv_credentials, cache_discovery=False)

        # Call the Drive v3 API

        if grdv_root != 'root':
            results = service.files().list(
                q="mimeType = 'application/vnd.google-apps.folder' and trashed = false and name='%s' and '%s' in parents" % (
                folder_name, grdv_root), pageSize=10, fields="nextPageToken, files(id, name)").execute()

        elif grdv_root == 'root':
            results = service.files().list(
                q="mimeType = 'application/vnd.google-apps.folder' and trashed = false and name='%s'" % (
                    folder_name), pageSize=10, fields="nextPageToken, files(id, name)").execute()

        items = results.get('files', [])

        if not items:
            LoggingMixin().log.warning("%s folder not found ! ", folder_name)
            return False
        else:
            return True

        # except errors.HttpError as e:
        #     LoggingMixin().log.error(str(e))

    def __is_file_available(self, file_name):

        service = build('drive', 'v3', credentials=self.gdrv_credentials, cache_discovery=False)

        # Call the Drive v3 API
        results = service.files().list(
            q="mimeType != 'application/vnd.google-apps.folder' and trashed = false and name='%s'" % (file_name),
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            LoggingMixin().log.warning("%s file not found !", file_name)
            return False
        else:
            return True

    def __create_folder(self, folder_name, parent=None):

        if parent != None:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent]
            }
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
            }
        drive_service = build('drive', 'v3', credentials=self.gdrv_credentials, cache_discovery=False)
        file = drive_service.files().create(body=file_metadata, fields='id').execute()

    def __get_file_id(self, file_name):

        service = build('drive', 'v3', credentials=self.gdrv_credentials, cache_discovery=False)

        # Call the Drive v3 API
        results = service.files().list(
            q="mimeType != 'application/vnd.google-apps.folder' and trashed = false and name='%s'" % (file_name),
            pageSize=10, fields="nextPageToken, files(id, name)").execute()

        items = results.get('files', [])

        if not items:
            LoggingMixin().log.warning('%s no file found !', file_name)
            return 0
        else:
            for item in items:
                return item['id']

    def __get_folder_id(self, folder_name):

        service = build('drive', 'v3', credentials=self.gdrv_credentials, cache_discovery=False)

        # Call the Drive v3 API
        results = service.files().list(
            q="mimeType = 'application/vnd.google-apps.folder' and trashed = false and name='%s'" % (folder_name),
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            LoggingMixin().log.warning('%s no folder found !', folder_name)
            return 0
        else:
            for item in items:
                return item['id']

    def __delete_file(self, file):
        """Permanently delete a file, skipping the trash.

        Args:
          service: Drive API service instance.
          file_id: ID of the file to delete.
        """
        service = build('drive', 'v3', credentials=self.gdrv_credentials, cache_discovery=False)

        # Call the Drive v3 API
        results = service.files().list(
            q="mimeType != 'application/vnd.google-apps.folder' and trashed = false and name='%s'" % (file),
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        # try:
        for item in items:
            service.files().delete(fileId=item['id']).execute()
            LoggingMixin().log.info(u'{0} ({1}) deleted successfully'.format(item['name'], item['id']))

        # except errors.HttpError as error:
        #     LoggingMixin().log.error(str(error))


class ServiceNow2GDRVTransOperatorException(Exception):
    pass
