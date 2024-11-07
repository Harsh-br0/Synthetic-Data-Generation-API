from .base_exception import BaseAppException


class MongoException(BaseAppException):
    "Base Exception for Mongo related issues."


class AuthFailureException(MongoException):
    "Exception related to auth issues with mongo db."


class DBNotInitialized(MongoException):
    "Exception raised when db connection is not ready."


class InvalidObjectId(MongoException):
    "Exception raised when invalid object id passed."


class ConfigException(MongoException):
    "Exception raised for config related issues with mongo."


class ConnectionFailedException(MongoException):
    "Exception raised for connection related issues with mongo."


class OperationFailedException(MongoException):
    "Exception raised on operation failure."
