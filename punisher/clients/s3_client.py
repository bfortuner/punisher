import boto3
import punisher.config as cfg
import punisher.constants as c


def get_client():
    return boto3.client('s3', aws_access_key_id=cfg.AWS_ACCESS_KEY,
                        aws_secret_access_key=cfg.AWS_SECRET_KEY)

def get_resource():
    return boto3.resource('s3', aws_access_key_id=cfg.AWS_ACCESS_KEY,
                          aws_secret_access_key=cfg.AWS_SECRET_KEY)

def get_buckets():
    return get_client().list_buckets()

def get_object_str(key, bucket=cfg.S3_BUCKET):
    s3 = get_resource()
    obj = s3.Object(bucket, key)
    return obj.get()['Body'].read().decode('utf-8')

def list_files(prefix='', bucket=cfg.S3_BUCKET):
    s3 = get_client()
    objs = s3.list_objects(Prefix=prefix, Bucket=bucket)
    keys = []
    for obj in objs['Contents']:
        if obj['Key'] != prefix+'/':
            keys.append(obj['Key'])
    return keys

def download_file(dest_fpath, s3_fpath, bucket=cfg.S3_BUCKET):
    get_client().download_file(Filename=dest_fpath,
                               Bucket=bucket,
                               Key=s3_fpath)

def upload_file(src_fpath, s3_fpath, bucket=cfg.S3_BUCKET):
    get_client().upload_file(Filename=src_fpath,
                             Bucket=bucket,
                             Key=s3_fpath)

def get_download_url(s3_path, bucket=cfg.S3_BUCKET, expiry=86400):
    return get_client().generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket,
                'Key': s3_path},
        ExpiresIn=expiry
    )

def delete_object(bucket, key):
    return get_client().delete_object(
        Bucket=bucket,
        Key=key
    )
