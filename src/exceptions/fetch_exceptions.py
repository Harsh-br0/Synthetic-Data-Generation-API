from . import BaseAppException


class FetchException(BaseAppException):
    "Base Exception related to fetch function."


class LengthException(FetchException):
    "Exception related to content length issues."


class ContentNotFound(FetchException):
    "Exception related to empty content in fetched resource."


class HTTPStatusException(FetchException):
    "Exception related to unsuccessful status codes returned in response."


class InvalidURLExcption(FetchException):
    "Exception raised on invalid URLs."


class NetworkTimeoutException(FetchException):
    "Exception related to timeout related issues."


class ProtocolViolationException(FetchException):
    "Exception raised when server violates the protocol."


class NetworkException(FetchException):
    "Exception related to network related issues."


class DecodingException(FetchException):
    "Exception related to decoding issues with response."
