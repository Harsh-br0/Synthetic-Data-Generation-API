from typing import BinaryIO

import boto3
from botocore.exceptions import ConnectionError

from ..decorators import handle_errors, retry
from ..exceptions.common import ConfigException
from .errors import errors_map
from .utils import get_bucket


class Bucket:
    _session = None
    _name = None

    def __init__(self, name: str = None) -> None:
        if name is None:
            name = self._name

            if name is None:
                raise ConfigException("S3 bucket name is not provided.")

        if self._session is None:
            raise ConfigException(
                "S3 Session is not available for use, are there any creds provided?"
            )

        self._resource = get_bucket(self._session, name)

    @handle_errors(errors_map)
    @retry((ConnectionError,))
    def upload_file(self, key: str, file: BinaryIO):
        self._resource.upload_fileobj(file, key)
        file.close()

    @classmethod
    def set_bucket_session(cls, ses: boto3.Session, name: str):
        cls._session = ses
        cls._name = name
