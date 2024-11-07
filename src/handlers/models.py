from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field

from ..defaults import CHAT_MODEL_MAX_TOKENS, CHAT_MODEL_NAME, CHAT_MODEL_TEMPERATURE


def strip_str(s: str):
    if isinstance(s, str):
        s = s.strip()
        if len(s) == 0:
            raise ValueError("Empty value passed.")
    return s


stripped_str = Annotated[str, BeforeValidator(strip_str)]


class S3Params(BaseModel):
    access_key: stripped_str
    secret_access_key: stripped_str
    region: stripped_str
    bucket_name: stripped_str


class BaseData(BaseModel):
    mongo_url: stripped_str
    s3_params: S3Params


class PostData(BaseData):
    "Data represented as json request body on post method for saving cookie."


class CookieData(BaseData):
    "Cookie data, passed along everywhere, even to browser but in encrypted form."


# Models capable of structured outputs,
Models = Literal["gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-mini", "gpt-4o-mini-2024-07-18"]


class OpenAIParams(BaseModel):
    model: Annotated[Models, BeforeValidator(strip_str)] = CHAT_MODEL_NAME
    max_completion_tokens: int = Field(CHAT_MODEL_MAX_TOKENS, ge=0)
    temperature: float = Field(CHAT_MODEL_TEMPERATURE, ge=0, le=2)
