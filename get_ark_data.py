# Script to generate input for the mint_arks_from_csv.py script accompanying
# larkm (https://github.com/mjordan/larkm/blob/main/extras/mint_arks_from_csv.py).

# Usage: python get_ark_data.py


import json
import csv
import logging
import traceback

import requests
from requests.exceptions import ConnectTimeout, ReadTimeout, ConnectionError
from rich.progress import track

policy = ""
metadata_value_separator = "|"

islandora_host = input(
    "Enter the hostname, including the leading https://, that you want to extract data from: "
).rstrip("/")
first_node_id = int(
    input(
        f"Enter the node ID of the earliest item in {islandora_host} you want to process: "
    )
)
last_node_id = int(
    input(
        f"Enter the node ID of the most recent item in {islandora_host} you want to process: "
    )
)

output_filename_base = islandora_host.replace("https://", "")
output_filename_base = output_filename_base.replace(".", "")

output_csv_filename = (
    f"{output_filename_base}_{first_node_id}_to_node_{last_node_id}.csv"
)
log_file_name = f"{output_filename_base}_{first_node_id}_to_{last_node_id}.log"

logging.basicConfig(
    filename=log_file_name,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


def get_id(node):
    """
    Generates a larkm identifier from the node's UUID.
    """
    uuid_without_hypens = node["uuid"][0]["value"].replace("-", "")
    return uuid_without_hypens[:12]


def get_when(node):
    """
    Forms a single string from all the values in the config["drupal_when_field"] field.
    :param node: dict - The node JSON converted to a dict.
    """
    if "field_edtf_date" not in node or len(node["field_edtf_date"]) == 0:
        return ""
    else:
        when_list = []
        for date in node["field_edtf_date"]:
            when_list.append(date["value"])
        return metadata_value_separator.join(when_list)


def get_who(node):
    """
    Forms a single string from the term names for the terms identified in the Drupal field
    identified in node["field_linked_agent"], which is a typed relation field.
    :param node: dict - The node JSON converted to a dict.
    """
    if "field_linked_agent" not in node or len(node["field_linked_agent"]) == 0:
        return ""
    else:
        who_list = []
        for who in node["field_linked_agent"]:
            # Skip deleted terms.
            if "target_type" not in who:
                return ""
            term_id = who["target_id"]
            if term_id in field_linked_agent_cache.keys():
                who_list.append(field_linked_agent_cache[term_id])
            else:
                url = (
                    f'{islandora_host.rstrip("/")}/taxonomy/term/{term_id}?_format=json'
                )
                try:
                    r = requests.get(url)
                    term_entity_json = r.text
                    term_entity_dict = json.loads(term_entity_json)
                    term_name = term_entity_dict["name"][0]["value"]
                    who_list.append(term_name)
                    field_linked_agent_cache[term_id] = term_name
                except Exception as ex:
                    logging.error(
                        f"Attempt to fetch term name for {url} failed. Status code: {r.status_code}, exception: {ex}"
                    )
                    return ""
        return metadata_value_separator.join(who_list)


field_linked_agent_cache = dict()
ouput_csv_headers = [
    "target",
    "uuid",
    "title",
    "who",
    "when",
    "policy",
]
output_file_handle = open(output_csv_filename, "w", encoding="utf-8")
writer = csv.DictWriter(
    output_file_handle, fieldnames=ouput_csv_headers, lineterminator="\n"
)
writer.writeheader()

number_items_to_check = last_node_id - first_node_id
for nid in track(
    [n for n in range(first_node_id, last_node_id + 1)],
    description=f"Processing {number_items_to_check + 1} items...",
):
    node_url = f"{islandora_host}/node/{nid}?_format=json"
    output_row = dict()
    try:
        r = requests.get(node_url, timeout=50)
        if r.status_code == 200:
            try:
                node = json.loads(r.text)
            except json.decoder.JSONDecodeError as e:
                logging.error(f"Node {nid} JSON error: {e}")
                continue

            output_row = {
                "target": f"{islandora_host}/node/{nid}",
                "title": node["title"][0]["value"],
                "uuid": get_id(node),
                "who": get_who(node),
                "when": get_when(node),
                "policy": policy,
            }
            writer.writerow(output_row)
    except Exception as ex:
        logging.error(f"Exception processing node {nid}: ({traceback.format_exc()})")

output_file_handle.close()
