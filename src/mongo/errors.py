from pymongo.errors import (
    ConfigurationError,
    ConnectionFailure,
    InvalidURI,
    OperationFailure,
    PyMongoError,
)

from ..exceptions.mongo_exceptions import (
    ConfigException,
    ConnectionFailedException,
    MongoException,
    OperationFailedException,
)

errors_map = {
    ConfigurationError: lambda _: ConfigException(
        "Config issues with the provided mongo url, make sure that it's correct."
    ),
    InvalidURI: lambda _: ConfigException("provided mongo url was incorrect, recheck please."),
    ValueError: lambda _: ConfigException(
        "Unexpected value passed as mongo url, please recheck the url and"
        " make sure the username and password are url-encoded if they have special characters."
    ),
    ConnectionFailure: lambda _: ConnectionFailedException("Connection failure with mongo."),
    OperationFailure: lambda _: OperationFailedException("Operation failed with mongo db."),
    PyMongoError: lambda _: MongoException("Some issue occured with mongo."),
}
