import re

import httpx
from bs4 import BeautifulSoup
from httpx import (
    DecodingError,
    HTTPError,
    HTTPStatusError,
    InvalidURL,
    NetworkError,
    RemoteProtocolError,
    TimeoutException,
)

from ..decorators import handle_errors, retry
from ..defaults import MAX_FETCH_LENGTH
from ..exceptions.fetch_exceptions import (
    ContentNotFound,
    DecodingException,
    FetchException,
    HTTPStatusException,
    InvalidURLExcption,
    LengthException,
    NetworkException,
    NetworkTimeoutException,
    ProtocolViolationException,
)

URL_PATTERN = re.compile(
    r"^https?:\/\/(?:[a-zA-Z0-9-]+\.)*"  # scheme and sub-domain
    r"[a-zA-Z0-9-_]+\.[a-z]{2,7}"  # domain
    r"(?:\/[a-zA-Z0-9-_:+]+)*\/?"  # path
    r"(?:\?[a-zA-Z0-9-_]+=[a-zA-Z0-9-_]+(?:&[a-zA-Z0-9-_]+=[a-zA-Z0-9-_]+)*)?$",  # query params
    re.IGNORECASE,
)
# copy-able string for testing
# ^https?:\/\/(?:[a-zA-Z0-9-]+\.)*[a-zA-Z0-9-_]+\.[a-z]{2,7}(?:\/[a-zA-Z0-9-_:+]+)*\/?(?:\?[a-zA-Z0-9-_]+=[a-zA-Z0-9-_]+(?:&[a-zA-Z0-9-_]+=[a-zA-Z0-9-_]+)*)?$


class FetchWrapper:

    @staticmethod
    def is_url(s: str):
        s = s.rsplit("#", 1)[0]  # stripping off the url fragment as it wasn't sent to server

        if URL_PATTERN.fullmatch(s) is None:
            return False

        return True

    @staticmethod
    @handle_errors(
        {
            HTTPStatusError: lambda _: HTTPStatusException(
                "Received an unsuccessful status code while fetching this URl."
            ),
            InvalidURL: lambda _: InvalidURLExcption("Url is invalid."),
            TimeoutException: lambda _: NetworkTimeoutException("Request timed out."),
            NetworkError: lambda _: NetworkException(
                "Failed to retrive content from URl due to network related issues."
            ),
            RemoteProtocolError: lambda _: ProtocolViolationException(
                "Server violated the protocol by returning invalid response."
            ),
            DecodingError: lambda _: DecodingException(
                "Failed to decode the response returned by server."
            ),
            HTTPError: lambda _: FetchException("Error occured while fetching this URl."),
        }
    )
    @retry((TimeoutException, NetworkError))
    def fetch_url(url: str):
        with httpx.stream(
            "GET",
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/117.0.5938.62 Safari/537.36",
            },
            follow_redirects=True,
        ) as res:

            res.raise_for_status()

            if "html" not in res.headers.get("Content-Type", ""):
                raise ContentNotFound("HTML content not found in the URL.")

            length = int(res.headers.get("Content-Length", -1))

            content = b""
            if length > MAX_FETCH_LENGTH:
                raise LengthException("Content length is more than maximum fetch limit.")

            elif length == -1:
                body_length = 0
                for chunk in res.iter_bytes(7 * 1024):

                    body_length += len(chunk)
                    if body_length > MAX_FETCH_LENGTH:
                        raise LengthException("Content length is more than maximum fetch limit.")

                    content += chunk
            else:
                content = res.read()

            soup = BeautifulSoup(content, "lxml")
            if soup.body is None:
                raise ContentNotFound("No content found in the URL.")

            return soup.body.get_text("\n", True).strip()
