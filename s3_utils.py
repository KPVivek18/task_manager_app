import boto3
import uuid
from flask import current_app

def upload_file_to_s3(file_object, filename):
    s3 = boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    )

    bucket = current_app.config['AWS_BUCKET_NAME']
    unique_filename = f"{uuid.uuid4()}_{filename}"

    s3.upload_fileobj(
        fileobj=file_object,  # ✅ corrected lowercase
        Bucket=bucket,
        Key=unique_filename
    )

    file_url = f"https://{bucket}.s3.{current_app.config['AWS_REGION']}.amazonaws.com/{unique_filename}"
    return file_url
