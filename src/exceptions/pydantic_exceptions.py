from . import BaseAppException


class PydanticException(BaseAppException):
    "Exception raised on pydantic related issues."


class ValidationException(PydanticException):
    "Exception raised on data validation."


class SerializationException(PydanticException):
    "Exception raised on data serialization."
