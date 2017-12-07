import os
import json

import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload




# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This access scope grants read-only access to the authenticated user's Drive
# account.
SCOPES = ['https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

def get_authenticated_service():
    # Copy your credentials from the console
    with open(CLIENT_SECRETS_FILE) as data_file:
        data = json.loads(data_file.read())
    print()    
    CLIENT_ID = data["installed"]["client_id"]
    CLIENT_SECRET = data["installed"]["client_secret"]

    # Check https://developers.google.com/drive/scopes for all available scopes                                                               
    OAUTH_SCOPE = SCOPES

    # Redirect URI for installed apps                                                                                                         
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    # Create a credential storage object.  You pick the filename.
    storage = Storage('creds')

    # Attempt to load existing credentials.  Null is returned if it fails.
    credentials = storage.get()
    #print(credentials)
    # Only attempt to get new credentials if the load failed.
    if not credentials:
    # Run through the OAuth flow and retrieve credentials                                                                                 
        flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

        authorize_url = flow.step1_get_authorize_url()
        print ('Go to the following link in your browser: ' + authorize_url)
        code = input('Enter verification code: ').strip()

        credentials = flow.step2_exchange(code)
        storage.put(credentials)
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

##def list_drive_files(service, **kwargs):
##  results = service.files().list(
##    **kwargs
##  ).execute()
##
##  pp.pprint(results)

def uploadMedia(service):
    folder_id='1yDr8nyPS2EOUG0DVhcn6-fPqx_FLD-Gd'
    file_metadata = {'name': 'abc.jpeg', 'parents': [folder_id]}
    media = MediaFileUpload('office.jpg',mimetype='image/jpeg')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print (file.get('id'))

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  service = get_authenticated_service()
  #print(service)
  #list_drive_files(service,orderBy='modifiedByMeTime desc',pageSize=5)
  uploadMedia(service)
