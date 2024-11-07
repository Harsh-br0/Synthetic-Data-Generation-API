from pydantic_core import PydanticSerializationError, ValidationError
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from ..decorators import handle_errors, retry
from ..defaults import MONGO_COL_NAME, MONGO_DB_NAME
from ..exceptions.mongo_exceptions import DBNotInitialized
from ..exceptions.pydantic_exceptions import SerializationException, ValidationException
from .errors import errors_map
from .model import SyntheticDataDoc


class Database:
    _conn: MongoClient = None

    def __init__(self, db_name: str = None, col_name: str = None) -> None:
        if db_name is None:
            db_name = MONGO_DB_NAME

        if col_name is None:
            col_name = MONGO_COL_NAME

        self.db_name = db_name
        self.col_name = col_name

        if self._conn is None:
            raise DBNotInitialized("DB Connection not ready.")

        self._col = self._conn[db_name][col_name]

    @handle_errors(
        errors_map
        | {
            PydanticSerializationError: lambda _: SerializationException(
                "Data Serialization failed at mongodb insert operation."
            )
        }
    )
    @retry((ConnectionFailure,))
    def insert(self, doc: SyntheticDataDoc):
        self._col.insert_one(doc.model_dump(by_alias=True))

    @handle_errors(
        errors_map
        | {
            ValidationError: lambda e: ValidationException(
                f"Validation failed with data model: {e.title}"
            )
        }
    )
    @retry((ConnectionFailure,))
    def fetch(self, ids):
        ids_filter = {"_id": {"$in": list(ids)}}
        cursor = self._col.find(ids_filter)
        return list(map(SyntheticDataDoc.model_validate, cursor))

    @classmethod
    def set_connection(cls, client: MongoClient):
        cls._conn = client
