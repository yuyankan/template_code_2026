from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#first: enbalbe google drive api
#https://console.cloud.google.com/marketplace/product/google/drive.googleapis.com?q=search&referrer=search&inv=1&invt=Abz-IA&project=avy-apac-material-digital-data

# 第一次用会弹出浏览器登录
gauth = GoogleAuth()
gauth.CommandLineAuth()
#gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

# 上传图片文件
file = drive.CreateFile({'title': 'content.png'})
file.SetContentFile('content.jpg')
file.Upload()

# 设置公开可访问
file.InsertPermission({
    'type': 'anyone',
    'value': 'anyone',
    'role': 'reader'
})

print("图片链接:", file['alternateLink'])
