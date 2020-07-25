from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    """
    Media Storage Class to Upload to S3
    """
    location = 'media'
    file_overwrite = False