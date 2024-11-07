import boto3
from botocore.exceptions import ConnectionError

from ..decorators import handle_errors, retry
from ..exceptions.common import ConfigException
from ..exceptions.s3_exceptions import ClientException, InvalidRegionException
from ..handlers.models import S3Params
from .errors import errors_map


def create_session(data: S3Params):
    session = boto3.Session(data.access_key, data.secret_access_key)

    if data.region not in session.get_available_regions("s3"):
        raise InvalidRegionException(f"Invalid region name passed for s3: {data.region}")

    session = boto3.Session(data.access_key, data.secret_access_key, region_name=data.region)

    return session


@handle_errors(errors_map)
@retry((ConnectionError,))
def get_bucket(session: boto3.Session, bucket_name: str):
    bucket = session.resource("s3").Bucket(bucket_name)
    if bucket.creation_date is None:
        raise ConfigException(
            f"Bucket with name '{bucket.name}' doesn't exists or "
            "not permitted to access with provided credentials."
        )
    return bucket


@handle_errors(errors_map)
@retry((ConnectionError,))
def test_write(session: boto3.Session, bucket_name: str):
    bucket = get_bucket(session, bucket_name)
    bucket.put_object(Key="test_object_key.txt", Body="Test")


@handle_errors(errors_map)
@retry((ConnectionError,))
def test_read(session: boto3.Session, bucket_name: str):
    bucket = get_bucket(session, bucket_name)
    obj = bucket.Object("test_object_key.txt")
    content = obj.get()["Body"].read().decode("utf-8")
    if content != "Test":
        raise ClientException("Couldn't verify the session for s3 credentials.")


@handle_errors(errors_map)
@retry((ConnectionError,))
def cleanup(session: boto3.Session, bucket_name: str):
    bucket = get_bucket(session, bucket_name)
    bucket.Object("test_object_key.txt").delete()


def ensure_session(data: S3Params):
    session = create_session(data)
    test_write(session, data.bucket_name)
    test_read(session, data.bucket_name)
    cleanup(session, data.bucket_name)
    return session
