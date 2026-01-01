from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import os

# Google Drive API 权限范围
SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/gmail.send']# only send

token_file= 'token_drive_mail.json'

client_secret = 'token_drive_mail.json'

def get_token(SCOPES=SCOPES, token_file=token_file, client_secret=client_secret):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(client_secret, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 第一次运行会弹出浏览器登录 Google 账号
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
            
    # 保存登录凭证
    with open(token_file, 'w') as token:
        token_get = creds.to_json()
        token.write(token_get)
    return creds

    

if __name__ == '__main__':
    get_token()