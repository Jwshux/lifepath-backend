import os
import uuid
import hashlib

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config as BotoConfig
from flask import current_app
from werkzeug.utils import secure_filename


APK_CONTENT_TYPE = 'application/vnd.android.package-archive'

# Files larger than 16 MB use multipart upload automatically.
TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=16 * 1024 * 1024,
    multipart_chunksize=16 * 1024 * 1024,
    max_concurrency=4,
    use_threads=True,
)


def get_r2_client():
    account_id = current_app.config.get('R2_ACCOUNT_ID')
    access_key_id = current_app.config.get('R2_ACCESS_KEY_ID')
    secret_access_key = current_app.config.get(
        'R2_SECRET_ACCESS_KEY'
    )

    if not all([
        account_id,
        access_key_id,
        secret_access_key,
    ]):
        raise RuntimeError(
            'Cloudflare R2 credentials are not configured.'
        )

    return boto3.client(
        's3',
        endpoint_url=(
            f'https://{account_id}.'
            'r2.cloudflarestorage.com'
        ),
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name='auto',
        config=BotoConfig(
            signature_version='s3v4',
            retries={
                'max_attempts': 4,
                'mode': 'standard',
            },
        ),
    )


def get_bucket_name():
    bucket_name = current_app.config.get('R2_BUCKET_NAME')

    if not bucket_name:
        raise RuntimeError(
            'Cloudflare R2 bucket name is not configured.'
        )

    return bucket_name


def test_r2_connection():
    client = get_r2_client()

    client.head_bucket(
        Bucket=get_bucket_name(),
    )

    return True


def validate_apk_file(file):
    if not file or not file.filename:
        raise ValueError('An APK file is required.')

    safe_name = secure_filename(file.filename)

    if not safe_name:
        raise ValueError('The selected filename is invalid.')

    if os.path.splitext(safe_name)[1].lower() != '.apk':
        raise ValueError('Only APK files are allowed.')

    return safe_name

def calculate_file_metadata(file):
    if not file:
        raise ValueError('An APK file is required.')

    digest = hashlib.sha256()
    file_size = 0

    file.stream.seek(0)

    while True:
        chunk = file.stream.read(1024 * 1024)

        if not chunk:
            break

        file_size += len(chunk)
        digest.update(chunk)

    file.stream.seek(0)

    return file_size, digest.hexdigest()


def build_release_object_key(file_name):
    safe_name = secure_filename(file_name)

    return (
        f'releases/'
        f'{uuid.uuid4().hex}-'
        f'{safe_name}'
    )


def upload_apk(file, object_key):
    if not object_key:
        raise ValueError('An R2 object key is required.')

    client = get_r2_client()

    # Make sure reading begins at the start of the uploaded file.
    file.stream.seek(0)

    client.upload_fileobj(
        Fileobj=file.stream,
        Bucket=get_bucket_name(),
        Key=object_key,
        ExtraArgs={
            'ContentType': APK_CONTENT_TYPE,
            'ContentDisposition': (
                f'attachment; filename="{secure_filename(file.filename)}"'
            ),
        },
        Config=TRANSFER_CONFIG,
    )

    return object_key


def delete_object(object_key):
    if not object_key:
        return False

    client = get_r2_client()

    client.delete_object(
        Bucket=get_bucket_name(),
        Key=object_key,
    )

    return True


def generate_download_url(
    object_key,
    download_name='LifePATH.apk',
    expires_in=120,
):
    if not object_key:
        raise ValueError('An R2 object key is required.')

    safe_download_name = secure_filename(
        download_name
    ) or 'LifePATH.apk'

    client = get_r2_client()

    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': get_bucket_name(),
            'Key': object_key,
            'ResponseContentDisposition': (
                f'attachment; filename="{safe_download_name}"'
            ),
            'ResponseContentType': APK_CONTENT_TYPE,
        },
        ExpiresIn=expires_in,
    )