from .base_exception import BaseAppException


class OpenAIException(BaseAppException):
    "Base Exception class responsible for openai related issues."


class AIResponseException(OpenAIException):
    "Exception responsible for AI generated response having refusals or other reasons."


class AuthException(OpenAIException):
    "Exception responsible for auth related issues with OpenAI."


class ConnectionFailure(OpenAIException):
    "Exception responsible for connection issues with OpenAI."


class TimeoutException(OpenAIException):
    "Exception raised on timeouts with openAI."


class BadRequestException(OpenAIException):
    "Exception raised for bad requests."


class InternalServerException(OpenAIException):
    "Exception raised if OpenAI faced some internal issues."


class RateLimitException(OpenAIException):
    "Exception raised for rate limit issues."


class PermissionDeniedException(OpenAIException):
    "Exception raised when there are permission issues with the OpenAI resource."


class UnprocessableEntityException(OpenAIException):
    "Exception raised if the API couldn't process the request."


class APIStatusException(OpenAIException):
    "Exception raised for API status codes with 4xx/5xx values."


class NotFoundException(OpenAIException):
    "Exception raised for invalid or inexistent resource on OpenAI."


class ConflictException(OpenAIException):
    "Exception raised for conflicted requests with OpenAI."
