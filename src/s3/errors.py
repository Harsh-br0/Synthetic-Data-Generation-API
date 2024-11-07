from botocore.exceptions import ClientError, ConnectionError, InvalidRegionError

from ..exceptions.s3_exceptions import (
    ClientException,
    ConnectionException,
    InvalidRegionException,
)


def handle_client_error(e: ClientError):
    codes = {
        "NoSuchBucket": "Bucket does not exist, create it first.",
        "NoSuchKey": "Requested Object key does not exist.",
        "AccessDenied": "The credentials does not have access to bucket or object.",
        "AccountProblem": "There is a problem with your AWS account"
        " that prevents the operation from completing successfully.",
        "AllAccessDisabled": "All access to this Amazon S3 resource has been disabled.",
        "EntityTooLarge": "Proposed upload exceeds the maximum allowed object size.",
        "InvalidAccessKeyId": "The AWS access key ID that you provided is not valid.",
        "InvalidBucketName": "The specified bucket is not valid.",
        "InvalidSignature": "The AWS secret access key is not valid.",
        "SignatureDoesNotMatch": "The AWS secret access key is not valid.",
        "MaxMessageLengthExceeded": "The S3 request was too large to handle.",
        "MethodNotAllowed": "The specified method is not allowed against this S3 resource.",
    }

    if e.response is None or "Error" not in e.response or "Code" not in e.response["Error"]:
        return ClientException("Can't know the error code, some unknown error occured with s3.")

    msg = codes.get(e.response["Error"]["Code"], e.response["Error"]["Message"])

    return ClientException(f"Faced an issue with S3: {msg}")


errors_map = {
    ConnectionError: lambda _: ConnectionException(
        "There was an Connection issue while connecting to S3."
    ),
    # client error is like base error from s3 so it accounts for most of errors
    ClientError: handle_client_error,
    InvalidRegionError: lambda e: InvalidRegionException(
        "Invalid region name passed for s3:"
        f" {e.kwargs.get('region_name', 'Could not find region name.')}"
    ),
}
