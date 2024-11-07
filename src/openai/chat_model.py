import openai
from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)

from ..decorators import handle_errors, retry
from ..exceptions.openai_exceptions import (
    AIResponseException,
    APIStatusException,
    AuthException,
    BadRequestException,
    ConflictException,
    ConnectionFailure,
    InternalServerException,
    NotFoundException,
    OpenAIException,
    PermissionDeniedException,
    RateLimitException,
    TimeoutException,
    UnprocessableEntityException,
)
from ..handlers.models import OpenAIParams
from ..logging import logger

log = logger(__name__)


class ChatModel:
    params = OpenAIParams()

    def __init__(self, params: OpenAIParams = None) -> None:
        if params is not None:
            self.params = params

    @handle_errors(
        {
            APIConnectionError: lambda _: ConnectionFailure("Connection failure with OpenAI API."),
            APITimeoutError: lambda _: TimeoutException("Operation timed out with OpenAI API."),
            BadRequestError: lambda _: BadRequestException("Bad Request passed to OpenAI API."),
            InternalServerError: lambda _: InternalServerException(
                "OpenAI Server is having some internal issues."
            ),
            NotFoundError: lambda e: NotFoundException(
                "This resource does not exist on openAI:"
                f" {(e.body or {'message':'Response was None from openAI'})['message']}"
            ),
            ConflictError: lambda _: ConflictException(
                "Resource conflict occured, Try again later."
            ),
            RateLimitError: lambda _: RateLimitException("OpenAI API is rate limited."),
            AuthenticationError: lambda _: AuthException(
                "OpenAI API Key is Invalid or Expired, It need to be replaced with a new API Key."
            ),
            PermissionDeniedError: lambda _: PermissionDeniedException(
                "OpenAI API Key don't have permission to proceed with this request."
            ),
            UnprocessableEntityError: lambda _: UnprocessableEntityException(
                "OpenAI API couldn't process the request."
            ),
            APIStatusError: lambda _: APIStatusException(
                "Unsuccessful response code returned by OpenAI API."
            ),
            APIError: lambda _: OpenAIException("Some unexpected error occured with OpenAI API."),
        }
    )
    @retry((APIConnectionError, UnprocessableEntityError))
    def invoke(self, msgs, **kwargs):
        res = openai.chat.completions.create(messages=msgs, **self.params.model_dump(), **kwargs)

        log.info("OpenAI Token Usage: '%s'", res.usage.model_dump_json(indent=1))

        reasons = {
            "length": "Model reached the specified token limit.",
            "content_filter": "Model flagged the content as inappropriate.",
        }

        res = res.choices[0]

        if res.finish_reason != "stop":
            reason = reasons.get(res.finish_reason)

            if reason is None:
                log.error("Unknown AI Response reason: %s", res.finish_reason)
                reason = "Unknown Reason raised by OpenAI that led the response to be void."

            raise AIResponseException(reason)

        if res.message.refusal is not None:
            raise AIResponseException("Model refused with: " + res.message.refusal)

        return res.message.content

    @classmethod
    def set_params(cls, params: OpenAIParams):
        cls.params = params
