import os
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
from pydantic_core import PydanticSerializationError, ValidationError

from ..decorators import handle_errors
from ..defaults import COOKIE_DURATION
from ..exceptions.common import ConfigException
from ..exceptions.cookie_exceptions import (
    CookieExpiredException,
    InvalidCookieException,
)
from ..exceptions.pydantic_exceptions import SerializationException, ValidationException
from .models import CookieData


class EncryptedCookie:
    @handle_errors(
        {ValueError: lambda _: ConfigException("Provided key for cookie encryption is invalid.")}
    )
    def __init__(self, key: str = None) -> None:
        if key is None:
            key = os.environ.get("ENCRYPTED_COOKIE_KEY")

        if key is None:
            raise ConfigException("No key found for encrypting cookies.")

        self._encrypter = Fernet(key)

    @handle_errors(
        {
            InvalidToken: lambda _: InvalidCookieException(
                "Cookie data is invalid, Signature verification failed."
            ),
            ValidationError: lambda e: ValidationException(
                f"Validation failed with data model: {e.title}"
            ),
        }
    )
    def decrypt(self, data: str) -> CookieData:
        time = self._encrypter.extract_timestamp(data)
        if (datetime.now() - datetime.fromtimestamp(time)).total_seconds() >= COOKIE_DURATION:
            raise CookieExpiredException("Cookie is expired.")

        data = self._encrypter.decrypt(data)
        return CookieData.model_validate_json(data)

    @handle_errors(
        {
            PydanticSerializationError: lambda _: SerializationException(
                "Data Serialization failed at mongodb insert operation."
            ),
            ValidationError: lambda e: ValidationException(
                f"Validation failed with data model: {e.title}"
            ),
        }
    )
    def encrypt(self, data: dict) -> str:
        data = CookieData.model_validate(data)
        data = data.model_dump_json()
        return self._encrypter.encrypt(data.encode("utf-8")).decode("utf-8")
