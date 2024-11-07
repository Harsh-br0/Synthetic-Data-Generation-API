from . import BaseAppException


class BaseS3Exception(BaseAppException):
    "Base error class for S3 related errors."


class ClientException(BaseS3Exception):
    "Error class for client related errors."


class ConnectionException(BaseS3Exception):
    "Error raised for connection related issues."


class InvalidRegionException(BaseS3Exception):
    "Error raised for invalid region."
