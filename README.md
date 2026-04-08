A set of scripts to use with Islandora Workbench to assign ARKs to objects created during Workbench `create` tasks and to automate population of larkm with those ARKs:

- `larkm_populate_node.py`: This CSV preproceessor script assigns a larkm-compliant identifier to each node.
- `larkm_persist_to_queue.py`: This post-node-create script persists the node ID and data used in the ARK to a task queue.
- `larkm_populate_larkm.py`: This shutdown script iterates through the queue and registers the ARK with larkm.

## Requirements

- [Islandora Workbench](https://mjordan.github.io/islandora_workbench_docs/)
- An operating [larkm](https://github.com/mjordan/larkm) ARK manager/resolver

## Installation

Run `python -m pip install .`

## Usage

All three of the included scripts are Islandora Workbench "[hook](https://mjordan.github.io/islandora_workbench_docs/hooks/)" scripts (one CSV preproceessor script, one post-node-create scripts, and one shutdown script). They are configured in your Workbench config file as documented below and work in tandem to populate your Islandora objects with ARKs and to also persist the ARKs in a larkm instance. When correctly configured, these scripts automate this process within a Workbench job.

In addition to the configuration settings described below, you will need to make sure that the IP address of the computer running Islandora Workbench is included in the larkm configuration setting "trusted_ips".

## Configuration

Two sections of your Workbench config file need to be configured: 1) the hooks and 2) the settings for the hook scripts.

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


## License

MIT
