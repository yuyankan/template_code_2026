from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import tooken_google_api as tga

# Google Drive API 权限范围


def write2drive(creds,file_name):

    # 连接到 Google Drive
    service = build('drive', 'v3', credentials=creds)

    # 要上传的文件
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_name, resumable=True)

    # 上传
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file['id']
    print('✅ 上传成功:', file)

    # 设置公开访问权限: not able todo this
    #permission = {
    #    'type': 'anyone',
    #    'role': 'reader',
    #}
    #service.permissions().create(fileId=file_id, body=permission).execute()
    #print('🌐 文件已设为公开访问')

def work(file_name= 'image.jpg'):
    # Gmail API 范围（用于发送邮件）
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    token_file= 'token_drive_mail.json'
    client_secret = 'token_drive_mail.json'

    # ---------------------
    # 1. 授权 Gmail API
    # ---------------------
    creds = tga.get_token(SCOPES=SCOPES, token_file=token_file, client_secret=client_secret)

    # 要上传的文件
    file_name = 'image.jpg'
    write2drive(creds, file_name)

if __name__ == '__main__':
    work()