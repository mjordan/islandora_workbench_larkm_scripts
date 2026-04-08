#!/usr/bin/env python3

"""Islandora Workbench field preprocessor script that composes ARK identifiers for nodes
and adds them to the input CSV. Works in conjuction with the larkm_post_node_create.py
and larkm_shutdown_script.py scripts.
"""

import sys
import uuid
import logging

from ruamel.yaml import YAML

input = sys.argv[2].strip()
config_file_path = sys.argv[3].strip()

yaml = YAML()
with open(config_file_path, "r") as stream:
    config = yaml.load(stream)

logging.basicConfig(
    filename=config["arks_log_file_path"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


def generate_identifier():
    """
    Generates a larkm identifier from a UUIDv4.
    """
    uuid_without_hypens = str(uuid.uuid4()).replace("-", "")
    return uuid_without_hypens[:12]


ark_url = f'{config["larkm_host"].rstrip("/")}/ark:{config["larkm_naan"]}/{config["larkm_shoulder"]}{generate_identifier()}'

print(ark_url)
