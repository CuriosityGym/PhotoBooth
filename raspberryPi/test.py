import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

def list_drive_files(service, **kwargs):
  results = service.files().list(
    **kwargs
  ).execute()

# Copy your credentials from the console                                                                                                  
CLIENT_ID = '898759991079-5bpmv2jpk7sf9p5371crssvegglg8gr2.apps.googleusercontent.com'
CLIENT_SECRET = 'Ubw_HE1igxduAt-yeXwWezHC'

# Check https://developers.google.com/drive/scopes for all available scopes                                                               
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps                                                                                                         
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Create a credential storage object.  You pick the filename.
storage = Storage('creds')

# Attempt to load existing credentials.  Null is returned if it fails.
credentials = storage.get()

# Only attempt to get new credentials if the load failed.
if not credentials:

    # Run through the OAuth flow and retrieve credentials                                                                                 
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

    authorize_url = flow.step1_get_authorize_url()
    print ('Go to the following link in your browser: ' + authorize_url)
    code = input('Enter verification code: ').strip()

    credentials = flow.step2_exchange(code)
    storage.put(credentials)
    
list_drive_files(credentials,
                   orderBy='modifiedByMeTime desc',
                   pageSize=5)


  
