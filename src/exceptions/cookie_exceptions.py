from . import BaseAppException


class CookieException(BaseAppException):
    "Base Exception class for all cookie related issues."


class InvalidCookieException(CookieException):
    "Exception raised when an invalid cookie encountered."


class CookieExpiredException(CookieException):
    "Exception raised when the cookie is found expired."
