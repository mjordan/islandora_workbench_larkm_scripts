A set of scripts to use with Islandora Workbench to assign ARKs to objects created during Workbench `create` tasks and to automate population of larkm with those ARKs:

- `larkm_populate_node.py`: This CSV preproceessor script populates the input CSV with a larkm-compliant identifier for each node.
- `larkm_persist_to_queue.py`: This post-node-create script adds the node ID and data used in the ARK to a persistent queue.
- `larkm_populate_larkm.py`: This shutdown script iterates through the queue and registers the ARK with larkm.

This three-stage approach to creating ARKs for Islandora objects (populating the input CSV with ARKs, storing node IDs and ARK metadata in a persistent queue, and in a final step populating larkm from that queue) is intended to provide a fault-tolerant approach to assigning ARKs as early as possible in the objects' lifecycle, specifically without having to generate the ARKs after they are created and then update the objects with them. The ARKs are registered with larkm during the same Workbench job that creates the objects.

## Requirements

- [Islandora Workbench](https://mjordan.github.io/islandora_workbench_docs/)
- An operational [larkm](https://github.com/mjordan/larkm) ARK manager/resolver

> [!IMPORTANT]
> In addition to these requirements and the configuration settings described below, you will need to make sure that the IP address of the computer running Islandora Workbench is included in the larkm configuration setting "trusted_ips".

## Installation

Run `python -m pip install .`

## Usage

All three of the included scripts are Islandora Workbench "[hook](https://mjordan.github.io/islandora_workbench_docs/hooks/)" scripts (one CSV preproceessor script, one post-node-create scripts, and one shutdown script). They are configured in your Workbench config file as documented below and work in tandem to populate your Islandora objects with ARKs and to also persist the ARKs in a larkm instance. When correctly configured, these scripts automate this process within the initial `create` Workbench job.

These scripts can live outside your `islandora_workbench` directory, as long as the paths to them are reflected in the hook configuration settings. Depending on your system, you may also need to include the `python` interpreter (specific to your system) within the hook configuration settings, as illustrated below.

## Configuration

Two sections of your Workbench config file need to be configured: 1) the hooks and 2) the settings for the hook scripts:

### 1. Configuring the hooks

This configuration is no different from configuring any other Workbench "hook" scripts.

```
preprocessors: [field_identifier: 'python /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_populate_node.py']
node_post_create: ['python /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_persist_to_queue.py']
shutdown: ['python /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_populate_larkm.py']
```

### 2. Defining configuration settings for the scripts

The settings described below are not standard Workbench configuration settings; they need to be present in your Workbench config file only because the three scripts require them. Here is a block of sample settings, followed by an explanation of each setting:

```
arks_log_file_path: /home/mark/hacking/islandora_workbench_larkm_scripts/arks.log
drupal_ark_field: field_identifier
drupal_when_field: field_edtf_date
drupal_who_field: field_linked_agent
larkm_host: http://127.0.0.1:8000
larkm_api_key: 8d3ad3da-c3e8-4145-8fc4-b84f03a5c87a
larkm_naan: 19837
larkm_shoulder: x2
larkm_queue_path: /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_queue
larkm_multivalue_separator: ;
```

- `arks_log_file_path`: Absolute path to the log file created by the scripts.
- `drupal_ark_field`: The machine name of the field on your target content type where the node's ARK has been stored. Assumes that the ARK is the first (or only) value in the field.
- `drupal_when_field`: The machine name of the field on your target content type where the node's date is stored; multiple values from this field are joined into a single string using the character defined in the "larkm_multivalue_separator" setting. Assumes that the field is of EDTF type.
- `drupal_who_field`: The machine name of the field on your target content type where names are stored; multiple values from this field are joined into a single string using the character defined in the "larkm_multivalue_separator" setting. Assumes that the field is of typed relation type.
- `larkm_host`: The hostname of your larkm server, including the leading "https://". A trailing `/` is ignored.
- `larkm_api_key`: The API key to use when creating ARKs in larkm. Note that you will need to make sure that the IP address of the computer running Islandora Workbench is included in the larkm configuration setting "trusted_ips".
- `larkm_naan`: The NAAN to use.
- `larkm_shoulder`: The shoulder to use.
- `larkm_queue_path`: Absolute path to the persistent queue file.
- `larkm_multivalue_separator`: The character used to join repeated values in the "who" and "when" ARK fields.

A minimal, but complete, Workbench configuration file incorporating the two sections above is:

```
task: create
host: http://islandora.traefik.me/
username: admin
password: password
input_csv: metadata.csv
allow_adding_terms: true

preprocessors: ["field_identifier: python /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_populate_node.py"]
node_post_create: ["python /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_persist_to_queue.py"]
shutdown: ["python /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_populate_larkm.py"]

arks_log_file_path: /home/mark/hacking/islandora_workbench_larkm_scripts/arks.log
drupal_ark_field: field_identifier
drupal_when_field: field_edtf_date
drupal_who_field: field_linked_agent
larkm_host: http://127.0.0.1:8000
larkm_api_key: myapikey
larkm_naan: 19837
larkm_shoulder: x9
larkm_queue_path: /home/mark/hacking/islandora_workbench_larkm_scripts/larkm_queue
larkm_multivalue_separator: ;
```

## Populating larkm with ARKs for existing Islandora nodes

As explained above, configuring `larkm_populate_node.py`, `larkm_persist_to_queue.py`, and `larkm_populate_larkm.py` as Workbdench hook scripts registers ARKs in larkm at the time the Islandora nodes are created. But what if you want to create ARKs for existing nodes and register them with larkm?

This retroactive job can be accomplished by using the `mint_arks_from_csv.py` helper script that is part of the larkm Github repo. That script takes a CSV file and either populates larkm (or optionally populates the SQLite database that larkm uses as a datastore). That script is not specific to Islandora, but to generate the Islandora-specific input data for that script, included in this Github repository is an additional script, `get_ark_data.py`. In other words, `get_ark_data.py` extracts the Islandora-specific data, which can be used as input for the general-purpose `mint_arks_from_csv.py` script.

The `get_ark_data.py` script prompts the user for an Islandora hostname, then a start-of-range node ID, and finally an end-of-range node ID. Running the ouput from ths script through `mint_arks_from_csv.py` populates larkm, and also generates an output CSV file that can be used, with some modification, as the input CSV for a Workbench `update` task to persist the ARKs back into the Islandora objects. The specifics of this last step will depend on your local Islandora field configuration (e.g. which field to update with the ARKs) but all the necessary data is in the `mint_arks_from_csv.py` output CSV.

## Using this approach with ARK managers other than larkm

The only script that interacts with larkm is `larkm_populate_larkm.py`, and that interaction is limited to using larkm's REST interface to persist the ARKs. Adapting this pattern for use with other ARK managers with REST interfaces, such as UT Scarborough's [ARKs Service](https://github.com/digitalutsc/arks-service/wiki), will likely only modifying the `larkm_populate_larkm.py` script to issue the required HTTP requests.


## License

MIT
