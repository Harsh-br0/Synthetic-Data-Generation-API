from bson import ObjectId
from bson.errors import InvalidId
from httpx import URL
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo.uri_parser import parse_uri

from ..decorators import handle_errors, retry
from ..defaults import MONGO_CONNECTION_TIMEOUT, MONGO_DB_NAME
from ..exceptions.mongo_exceptions import AuthFailureException, InvalidObjectId
from .errors import errors_map


@handle_errors({InvalidId: lambda _: InvalidObjectId("Invalid Id Passed.")})
def make_id(id: str = None):
    return ObjectId(id)


@handle_errors(errors_map)
def validate_url(url: str):
    url = URL(url)

    blacklist_kw = ("tls", "ms", "file")
    for key in url.params.keys():
        for kw in blacklist_kw:
            if kw in key.lower():
                url = url.copy_with(params=url.params.remove(key))

    url = str(url)

    parse_uri(url)  # raises config error which is handled

    return url


@handle_errors(
    errors_map
    | {
        OperationFailure: lambda _: AuthFailureException(
            "Bad Auth with mongo while trying to authenticate, please recheck the entered url."
        ),
    }
)
@retry((ConnectionFailure,))
def create_connection(url: str):
    url = validate_url(url)
    client = MongoClient(url, serverSelectionTimeoutMS=MONGO_CONNECTION_TIMEOUT)
    client.admin.command("ping")
    return client


@handle_errors(
    errors_map
    | {
        OperationFailure: lambda _: AuthFailureException(
            "Bad Auth with mongo while performing write operation,"
            " please check if url is correct or have proper write permission on this url."
        ),
    }
)
@retry((ConnectionFailure,))
def test_write(client: MongoClient):
    col = client[MONGO_DB_NAME]["test_col"]
    col.insert_one({"ok": True})
    col.drop()


def ensure_connection(url: str):
    client = create_connection(url)
    test_write(client)
    return client
