
import logging
import logging.config
import os
import sys
import tomllib as toml
from importlib import reload

from box import Box
from dotenv import load_dotenv

load_dotenv(".env")

with open("config.toml", "rb") as f:
    config = Box(toml.load(f))

if config.credentials.api_token == "" and "SECRET" in os.environ:
    config.credentials.api_token = os.environ["SECRET"]

else:
    raise ValueError(
        "Must supply 'api_token' in config.toml or as environment variable SECRET"
    )

def get_logging_config(): 
    with open("logging.toml", "rb") as f:
        config = toml.load(f)
    return config

logging.config.dictConfig(get_logging_config())