from typing import Annotated, Optional

from fastapi import Cookie, HTTPException, Query, status

from ..mongo.db import Database
from ..mongo.utils import ensure_connection
from ..openai.chat_model import ChatModel
from ..s3.bucket import Bucket
from ..s3.utils import ensure_session
from .encrypted_cookie import EncryptedCookie
from .models import CookieData, OpenAIParams


def utilise_cookie(data: CookieData):
    client = ensure_connection(data.mongo_url)
    Database.set_connection(client)

    session = ensure_session(data.s3_params)
    Bucket.set_bucket_session(session, data.s3_params.bucket_name)


def cookie_dependency(sid: Annotated[Optional[str], Cookie(include_in_schema=False)] = None):
    if sid is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Valid cookie not found, make sure to login first."
        )

    cookie = EncryptedCookie()
    data = cookie.decrypt(sid)
    utilise_cookie(data)


def openai_params_dependency(model_params: Annotated[OpenAIParams, Query()]):
    ChatModel.set_params(model_params)
