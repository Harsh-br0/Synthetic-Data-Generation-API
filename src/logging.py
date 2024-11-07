import logging

logging.basicConfig(
    level="INFO",
    style="{",
    format="{asctime} - {levelname}({levelno}) : {filename}(Line {lineno}) : {message}",
)


def logger(name=None):
    return logging.getLogger(name)
