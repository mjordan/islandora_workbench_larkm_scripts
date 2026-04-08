"""Sample script to process items in the Persist Queue populated by the
workbench_queue_sample_enqueue_node_id.py script.
"""

import sys
import logging
import json

from ruamel.yaml import YAML
import requests
import persistqueue

config_file_path = sys.argv[1].strip()

yaml = YAML()
with open(config_file_path, "r") as stream:
    config = yaml.load(stream)

logging.basicConfig(
    filename=config["arks_log_file_path"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

q = persistqueue.SQLiteAckQueue(config["larkm_queue_path"], auto_commit=True)

if q.empty() is True:
    message = "larkm ARK creation queue is empty."
    logging.info(message)
    sys.exit(message)

larkm_host = config["larkm_host"].rstrip("/")
endpoint = f"{larkm_host}/larkm"
headers = {"Content-Type": "application/json", "Authorization": config["larkm_api_key"]}

queue_size = q.qsize()
while queue_size > 0:
    item = q.get()
    logging.info(f"Item read from queue: {item}")
    if len(item["ark"]) == 0:
        queue_size -= 1
        logging.warning(
            f'Queue item for node {item["node_id"]} did not contain an ARK.'
        )
        continue
    target = f'{config["host"].rstrip("/")}/node/{item["node_id"]}'
    identifier = item["ark"][-12:]
    larkm_url = f'{larkm_host}/ark:{config["larkm_naan"]}/{config["larkm_shoulder"]}{identifier}'
    larkm_data = {
        "naan": str(config["larkm_naan"]),
        "shoulder": str(config["larkm_shoulder"]),
        "identifier": identifier,
        "what": item["title"],
        "when": item["when"],
        "who": item["who"],
        "target": target
    }

    try:
        r = requests.post(endpoint, json=larkm_data, headers=headers)
        if r.status_code == 201:
            logging.info(
                f"ARK for {target} successfully persisted to larkm at {larkm_url}"
            )
            q.ack(item)
        else:
            logging.error(
                f"ARK for {target} not persisted to larkm: status code: {r.status_code}, response body: {r.text}."
            )
            q.nack(item)
    except Exception as ex:
        logging.error(
            f'Attempt to persist ARK {item["ark"]} to larkm failed. Status code: {r.status_code}, exception: {ex}'
        )

    queue_size -= 1

q.clear_acked_data(keep_latest=0, max_delete=0)
logging.info(
    f'ARK creation queue at {config["larkm_queue_path"]} cleared, with {q.qsize()} items remaining.'
)
