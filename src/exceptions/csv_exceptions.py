from .base_exception import BaseAppException


class CSVException(BaseAppException):
    "Base CSV Exception."


class InvalidCSVException(CSVException):
    "Exception raised for invalid CSV."


class EmptyCSVException(CSVException):
    "Exception raised for empty csv."
