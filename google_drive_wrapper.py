from __future__ import print_function
import pickle
import os
import pathlib
import io
import shutil
import sys
from googleapiclient.discovery import build, MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from traceback import print_exc


class google_drive():
    def __init__(self):
        """
        Initialize your Google Drive class and ensure you are authenticated.
        """
        self.drive_service = self.authenticate()

    def authenticate(self, SCOPES=["https://www.googleapis.com/auth/drive"], oauth_json_file="", pickle_file=""):
        """
        Authenticate against Google Drive. If a valid pickle file is not found, a URL will be provided to login to your Google account.
        :param SCOPES: list: Scopes to be used with Google Drive class.
        :param oauth_json_file: string: File, with path, to use for Oauth.
        :param pickle_file: string: File, with path, to use for pickle file.
        :return: object:
        """
        if not oauth_json_file:
            oauth_json_file = pathlib.Path(os.path.dirname(os.path.abspath(__file__)) + "/" + "google_drive_key.json").as_posix()

        if not pickle_file:
            pickle_file = pathlib.Path(os.path.dirname(os.path.abspath(__file__)) + "/" + "token.pickle").as_posix()

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(oauth_json_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(pickle_file, 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def list_folder_content(self, parent_id="", page_size=10, _fields="nextPageToken, files(id, name, parents)"):
        """
        List all content in Google Drive.
        :param parent_id: string: Parent ID of folder you wish look into. If blank, entire drive will be searched.
        :param page_size: int: Number of results per page. Best to leave default.
        :param _fields: string: This is used by Google Drive API to set what items to return.
        :return: list: Nested list of dictionaries based on the _fields parameter. Example: {'id': 'file_id', 'name': 'file_name', 'parents': ['parent_id']}
        """
        _results = []

        if parent_id:
            query = "'{}' in parents".format(parent_id)
            results = self.drive_service.files().list(pageSize=page_size, fields=_fields, q=query).execute()
        else:
            results = self.drive_service.files().list(pageSize=page_size, fields=_fields).execute()

        while True:
            for i in results['files']:
                _results.append(i)

            if 'nextPageToken' not in results.keys():
                break

            if parent_id:
                results = self.drive_service.files().list(pageSize=page_size, fields=_fields, pageToken=results['nextPageToken'], q=query).execute()
            else:
                results = self.drive_service.files().list(pageSize=page_size, fields=_fields, pageToken=results['nextPageToken']).execute()

        return _results

    def find_file(self, parent_id="", file_id="", file_name=""):
        """
        Search for file based on provided information.
        :param parent_id: string: Parent ID to search in for file ID or name.
        :param file_id: string: File ID to search for.
        :param file_name: string: File name to search for.
        :return: dictionary: Example: {'id': 'file_id', 'name': 'file_name', 'parents': ['parent_id']}
        """
        for file in self.list_folder_content(parent_id, page_size=100):
            if file_id and file_id == file['id']:
                return file
            elif file_name and file_name == file['name']:
                return file

        return False

    def download_file(self, file_id: str, file_name_to_save_as: str):
        """
        Download a file from Google Drive and save it locally.
        :param file_id: string: File ID of file to download.
        :param file_name_to_save_as: string: Name to save file as in current directory.
        :return: boolean: True if file downloaded successfully, False if not.
        """
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False
        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            # Write the received data to the file
            with open(file_name_to_save_as, 'wb') as f:
                shutil.copyfileobj(fh, f)
            # Return True if file Downloaded successfully
            return True
        except:
            # G-Suite files should be downloaded using export, so if that is the case the warning message is printed.
            warns = 'Only files with binary content can be downloaded. Use Export with Docs Editors files.'
            if warns in sys.exc_info()[1].content.decode():
                print(warns)
            # json.loads(x[1].content.decode())['error']['errors'][0]['message']
            return False

    def upload_file(self, file_name: str, parent_id="", new_file_name=""):
        """
        Upload a local file to Google Drive.
        :param parent_id: string: Parent ID to search in for file ID or name.
        :param file_name: string: File name of local file to upload.
        :param new_file_name: string: File name of file when it is uploaded.
        :return: string: File ID of file that was uploaded.
        """
        if not new_file_name:
            new_file_name = file_name

        media = MediaFileUpload(file_name, resumable=True)
        file_metadata = {'name': file_name, 'mimeType': '*/*'}
        if parent_id:
            file_metadata['parents'] = [parent_id]
        media = MediaFileUpload(new_file_name, mimetype='*/*', resumable=True)
        try:
            return self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()['id']
        except:
            print(sys.exc_info())
            return False

    def delete_file(self, file_id):
        """
        Delete file in Google Drive based on the file ID.
        :param file_id: string: ID of file to delete.
        :return: boolean: True if successfully delete, False if not.
        """
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            return True
        except:
            print(sys.exc_info())
            return False

    def get_download_link(self, file_id):
        """
        Provide download link of file with file ID provided.
        :param file_id: string: File ID to put into download link.
        :return: string: Download link of file.
        """
        return "https://drive.google.com/file/d/{}/view?usp=sharing".format(file_id)

    def check_folder_exists(self, folder_name: str, parent_id=""):
        """
        Check if folder exists in directory.
        :param parent_id: string: Set parent directory.
        :param folder_name: string: Folder name to look for in directory.
        :return: dictionary: If found a dictionary is returned, False if not. Example: {'id': 'file_id', 'name': 'file_name', 'parents': ['parent_id']}
        """
        for folder in self.list_folder_content(parent_id=parent_id):
            if folder_name == folder['name']:
                return folder

        return False

    def create_folder(self, folder_name: str, parent_id=""):
        """
        Create a folder within a directory.
        :param parent_id: string: Directory to make the new folder in, blank its top directory.
        :param folder_name: string: Name of new folder.
        :return: string: Folder ID of newly created folder. False if not created.
        """
        folder_data = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }

        if parent_id:
            folder_data['parents'] = [parent_id]

        try:
            return self.drive_service.files().create(body=folder_data, fields='id').execute()['id']
        except:
            print(sys.exc_info())
            return False

    def check_create_folder(self, folder_name: str, parent_id=""):
        """
        Check to see if a folder exists, if not create it.
        :param parent_id: string: Directory to make the new folder in, blank its top directory.
        :param folder_name: string: Name of folder to look for and make.
        :return: dictionary: Dictionary of results. Example: {'id': 'file_id', 'name': 'file_name', 'parents': ['parent_id']}
        """
        ans = self.check_folder_exists(folder_name=folder_name, parent_id=parent_id)
        if ans:
            return ans
        else:
            return {'id': str(self.create_folder(folder_name=folder_name, parent_id=parent_id)), 'name': folder_name, 'parents': [parent_id]}


def main():
    google_drive().authenticate()


if __name__ == '__main__':
    main()
