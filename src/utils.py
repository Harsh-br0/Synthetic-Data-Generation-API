import base64
import binascii
import json
import os
from typing import Sequence

from .logging import logger

try:
    import dotenv

    from .defaults import CONFIG_FILE
except ImportError:
    dotenv = CONFIG_FILE = None

log = logger(__name__)


def ensure_envs(envs: Sequence[str], config_file_required=True):
    if config_file_required and (dotenv is None or not dotenv.load_dotenv(CONFIG_FILE)):
        exit(
            "Failed to load config file. "
            "Make sure that `python-dotenv` is installed and "
            f"the file '{CONFIG_FILE}' exists at current working directory."
        )

    dev_mode_var = os.environ.get(
        "DEV_MODE_CONFIG"
    )  # special env to have all vars in base64 format for developer convenience.

    if dev_mode_var is not None:
        try:
            config_string = base64.b64decode(dev_mode_var)
            config = json.loads(config_string)
            os.environ.update(config)

        except (binascii.Error, json.JSONDecodeError):
            log.error("DEV_MODE_CONFIG is invalid. Picking documented envs.")

        else:
            log.info("Loaded DEV_MODE_CONFIG into envs.")

    for env in envs:
        if os.getenv(env) is None:
            exit(f"Env '{env}' doesn't exists. Properly configure the env variables.")


def ensure_string_in_dict(d: dict):
    return {k: str(v) for k, v in d.items()}
