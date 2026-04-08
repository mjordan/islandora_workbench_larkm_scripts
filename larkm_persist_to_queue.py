#!/usr/bin/env python

"""Islandora Workbench post-node-create script that adds data to a persistent
   queue for use by the Workbench shutdown script larkm_create_arks.py script.
"""

import sys
import json
import logging

import persistqueue
import requests

from ruamel.yaml import YAML

config_file_path = sys.argv[1].strip()
http_response_code = sys.argv[2].strip()
http_response_body = sys.argv[3].strip()
entity = json.loads(http_response_body)

yaml = YAML()
with open(config_file_path, "r") as stream:
    config = yaml.load(stream)

logging.basicConfig(
    filename=config["arks_log_file_path"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


def get_erc_who(node):
    """
    Forms a single string from the term names for the terms identified in the Drupal field
    identified in config["drupal_who_field"], which is assumed to be a typed relation field.
    :param node: dict - The node JSON converted to a dict.
    """
    if len(entity[config["drupal_who_field"]]) == 0:
        return ""
    else:
        who_list = []
        for who in entity[config["drupal_who_field"]]:
            # Skip deleted terms.
            if "target_type" not in who:
                return ""
            url = f'{config["host"].rstrip("/")}/taxonomy/term/{who["target_id"]}?_format=json'
            try:
                r = requests.get(url)
                term_entity_json = r.text
                term_entity_dict = json.loads(term_entity_json)
                term_name = term_entity_dict["name"][0]["value"]
                who_list.append(term_name)
            except Exception as ex:
                logging.error(
                    f"Attempt to fetch term name for {url} failed. Status code: {r.status_code}, exception: {ex}"
                )
                return ""
        return config["larkm_multivalue_separator"].join(who_list)


def get_erc_when(node):
    """
    Forms a single string from all the values in the config["drupal_when_field"] field.
    :param node: dict - The node JSON converted to a dict.
    """
    if len(entity[config["drupal_when_field"]]) == 0:
        return ""
    else:
        when_list = []
        for date in entity[config["drupal_when_field"]]:
            when_list.append(date["value"])
        return config["larkm_multivalue_separator"].join(when_list)



# Main script logic.

ark_field = config["drupal_ark_field"]
if http_response_code == "201":
    data = dict()
    data["node_id"] = entity["nid"][0]["value"]
    data["title"] = entity["title"][0]["value"]
    # Assumes that the ARK is the first (or only) value in the field.
    if len(entity[config["drupal_ark_field"]]) > 0:
        data["ark"] = entity[config["drupal_ark_field"]][0]["value"]
    else:
        data["ark"] = ""
    if len(entity[config["drupal_when_field"]]) > 0:
        data["when"] = get_erc_when(entity)
    else:
        data["when"] = ""
    data["who"] = get_erc_who(entity)

    try:
        q = persistqueue.SQLiteAckQueue(config["larkm_queue_path"], auto_commit=True)
        q.put(data)
        logging.info(f"Data {data} persisted to queue.")
    except Exception as e:
        logging.error(e)
