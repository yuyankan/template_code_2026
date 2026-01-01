from google.cloud import storage
import pyodbc
import os
from datetime import timedelta


# 设置环境变量（只需设置一次）
# SET UP AND gcs_key in gcp: 
#1. enable in gcp: service account oauth: download gcp_key.json
#2. add in IAM: add this service account in IAM as at least edit role, so could upload doc
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcs_key.json'

#set proxy if have vpc
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:9000'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:9000'


def upload_image_and_get_signed_url(bucket_name, source_file_path, destination_blob_name, expiration_minutes=15):
    """上传图片并返回一个临时的签名 URL"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # 上传图片
    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded to {destination_blob_name}.")

    # 生成临时 URL（signed URL）
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )
    return url


def upload_image_only(bucket_name, source_file_path, destination_blob_name):
    """上传图片并返回一个临时的签名 URL"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    # blob: binary large object/for each bucket,  in bucket
    blob = bucket.blob(destination_blob_name)

    # 上传图片
    blob.upload_from_filename(source_file_path)

    print('pic uploaded')
    return 


def get_gcp_image_temp_url_only(bucket_name, destination_blob_name,expiration_minutes=15):
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    # blob: binary large object/for each bucket,  in bucket
    blob = bucket.blob(destination_blob_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )

    print(f"Generated signed URL (valid for {expiration_minutes} minutes): {url}")
    return url




    
if __name__=='__main__':
    # 配置
    BUCKET_NAME = 'image_bucket_yyk_202506'
    LOCAL_IMAGE_PATH = 'img.jpg'
    GCS_IMAGE_NAME = 'test/just_test.jpg' #place in bucket and new name in bucket
    # 用法示例
    bucket_name = BUCKET_NAME
    source_file_path = LOCAL_IMAGE_PATH
    destination_blob_name = GCS_IMAGE_NAME

    temp_url = upload_image_and_get_signed_url(bucket_name, source_file_path, destination_blob_name)
    print("临时访问链接:", temp_url)



