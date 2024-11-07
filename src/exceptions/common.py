from . import BaseAppException


class ConfigException(BaseAppException):
    "Exception related to config issues."


class DataTooShort(BaseAppException):
    "Exception raised when the data is smaller than specified limit."
