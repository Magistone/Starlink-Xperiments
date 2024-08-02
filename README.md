# Starlink framework for measurements
This framework is designed to be used as a platform to easily collect metrics about starlink and its network performance.
Even though it was originally designed for starlink only, it can be used for other purposes as well.
Developed as a Bachelor Thesis at Saarland university under the supervision of Dependable Systems Chair.

The framework utilizes two containers for to achieve the functionality - a database and a "runner" container. The runner container is responsible for the collection of data while the DB container is responsible for persistance of the data. A large part of the setup process is automated which reduces the number of steps needed to get running. 
Throughout the documentation you will come a lot across those 3 terms:
- `node`: A machine that collects data
- `control node`: A machine from which automation scripts are run. Controls the operation of nodes
- `experiment`: A configuration that is passed to nodes. The nodes then start data collection based on this configuration

The framework is written in python and uses ansible to automate tasks such as deployment and running experiments on nodes where the framework is running.
Each experiment is contained within its own module that can be easily changed/added or removed. The architecture of the framework does not require a chosen control node to be online at all times, instead, the control node pushes tasks to experiment nodes that are then run independently.

## Requirements
Control node: 
 - Python >= 3.10
 - Recommended: Ubuntu 22/24 LTS

Experiment nodes: 
 - Control node can establish SSH connection to it
 - Recommended: Ubuntu 22 LTS

Although Ubuntu 24 LTS was already available at the time of writing, `Python 3.12` introduced breaking changes that broke
some automation and experiment scripts on the experiment nodes. The automation specifically targets APT package manager. If you use other distributions,
you will likely need to edit some part of the automation yourself. Running Ubuntu 24 LTS on the experiment nodes will cause some 
scripts to fail.

## Setup

Before starting, clone this repository on the machine you will want to use as the control node.

1. Run `init_orchestrator.sh` on the machine that will act as the control node. 
It has the following effects:
    - Installs Ansible
    - Installs Docker
    - Generates SSH key
    - Creates docker image for nodes
> [!IMPORTANT]
> You will be asked twice for password - once the usual `sudo password` and second time for `BECOME password`. This is your `sudo password` as well,
> ansible calls it `BECOME password` and is required as it manages the docker installation.

2. To prepare everything for running the tool, do the following for every machine that is an `experiment node`:
    - Create a user (or use existing) on the experiment node
    - Use `ssh-copy-id -i ~/.ssh/starlinktool.pub [NODE]` from control node to use the generated key. You can choose to use a different ssh key or even different ssh key for every node.
    - Make sure the user has sudo privilleges

3. On control node edit `ansible/inventory.yml` using your nodes addresses and credentials.
    In case you are familiar with ansible, you can skip to step 4.

    All your experiment nodes should be listed in `ansible/inventory.yml`. In case something is unclear, please read the [official documentation](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#inventory-basics-formats-hosts-and-groups).

    There are 2 parts to pay attention to:

    - The hosts section lists individual nodes. The `node_name` will show in ansible log and is used for directory name when collecting data. `ansible_host` is the IP or Fully Qualified Domain Name (FQDN) to connect to the node. Additional custom variables as you need (e.g. `name`). These can be accessed for tags when deploying experiments. The syntax is as follows:
        ```yml
        node_name:
            custom_var: value
            ansible_host: IP or FQDN
        ```
        If you need to add more specific directive (i.e. different user or ssh key for one node) you can simply add that as ansible [overrides variables](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#how-variables-are-merged)
        ```yml
        node_name:
            custom_var: value
            ansible_host: IP or FQDN
            ansible_user: different_user
            ansible_ssh_private_key_file: ~/.ssh/different_private_key
        ```

    - The `vars` section applies to all hosts. The minimum config stored in `ansible/inventory.yml` stores there the SSH user, encrypted sudo password and which SSH key that are used by default if the configuration for a particular node does not specify it. 
        ```yml
        vars:
            ansible_ssh_private_key_file: ~/.ssh/starlinktool
            ansible_user: some_user
            ansible_become_password: !vault |
                $ANSIBLE_VAULT;1.1;AES256
                3233333538333634623161633032343731393436
                3137396232393163333966353236346536643738
                3338633464633161333338373164636333383566
                353130610a666263613964646564626561393764
        ```
> [!TIP]
> IPv6 addresses are globally adressable

> [!NOTE]
> The sudo password is encrypted using [vault](https://docs.ansible.com/ansible/latest/vault_guide/vault_encrypting_content.html#encrypting-individual-variables-with-ansible-vault). 
> This way different sudo passwords can be stored in the inventory and be protected by a single master password. If
> using encrypted variables like here, add `--ask-vault-pass` to be asked for the master password when running against the inventory.

4. Run the ansible playbook called `setup_node.yml` against your configured inventory. This will install all dependencies and start the tool:

    `ansible-playbook ./ansible/setup-node.yml -i ./ansible/inventory.yml`.

    If everything succeeds, your nodes are ready to receive experiment commands.

> [!NOTE]
> You have now completed the setup and the tool is running on your experiment nodes.
> You can now continue with running experiments.

## Experiments - How to
### Variables
When dealing with experiments, there are some variables that are up to you to use. The list of variables and conditions is listed below. The types are python/yaml types:

- module: `string`, required. Name of the experiment module without `.py` extension (e.g. `ip` for `ip.py`),
- start: `string`, optional. Start time in RFC7231 format (e.g. `Sun, 06 Nov 1994 08:49:37 GMT`)
- stop: `string`, required if forever is not `true`. Stop time in RFC7231 format (e.g. `Sun, 06 Nov 1994 08:49:37 GMT`)
- period: `float`, required. Sampling period in seconds
- forever: `boolean`, required. Defaults to `false`
- setup: `dictionary`, optional. Experiment dependent setup configuration
- config: `dictionary`, optional. Experiment dependent runtime configuration
- tags: `dictionary`, optional. Extra tags stored in metadata for the given experiment
- stow: `boolean`. Used by stow utility
- modules: `list[str]`. Used by install utility

### Deploying experiments
A sample playbook is provided in `ansible/sample_experiments.yml`.

Edit `stop` to be in the future and then use the following command to try it out:

`ansible-playbook ./ansible/sample_experiments.yml -i ./ansible/inventory.yml`

> [!TIP]
> You can use `dbg` boolean to print the configuration passed to the server without running the experiment

### The playbook 
You can easily create a set of experiments using playbooks. To do so, you can either use already included experiment modules or you can write your own (see below).
As explained previously, please remember that ansible [overrides variables](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#how-variables-are-merged)
and that it might affect the result.

For included experiment modules, all variables except for tags are overriden by ansible specification. If you want to control certain aspects of these experiment modules in your playbook, comment or delete the relevant part in the respective fragment stored in `ansible/fragments/jobs`.

> [!NOTE]
> Not all aspects are controlled by default

Included experiments:
 - Make sure that the aspects you want to control from your playbook are not included in the fragment (tags excluded). See overriding variables.
 - The included experiment modules support 'static' tags (fragment defined) and 'dynamic' tags (playbook defined). Ansible will merge them when both are desired. Use `tag_with` variable passed to the fragment to leverage this functionality. 

Custom experiments:
 - You will want to write an experiment module that does the custom thing. For that see [writing your own modules](#writing-your-own-experiment-modules)
 - To make deploying easier, a good idea is to make a fragment configuration that all included experiment modules have. You can find them in `ansible/fragments/jobs` directory
 - Your experiment modules might need dependencies that are not installed by default. If so, use the included [install utility](#install-utility) in your playbook
 - To deploy the custom experiment modules to all experiment nodes include `ansible/fragments/tasks/deploy_modules.yml` in your playbook
 - Run your custom experiment

> [!NOTE]
> To include `x` means using the directive `import_tasks: x` in the playbook.

> [!IMPORTANT]
> use `experiment_tags` when defining tags for custom experiments in your playbooks (see included fragments). The variable name `tags` conflicts with ansible tags

> [!TIP]
> If you get code 500 check your stop time. The scheduler doesn't verify that it is in the future, it only verifies that the sub-process has not crashed within the first second


### Collecting data from experiment nodes
Run the `collect_measurements.yml` playbook against your nodes. A new directory `collected_data` will be created.

Example: `ansible-playbook ./ansible/collect_measurements.yml -i ./ansible/inventory.yml`

Data format for a single entry:
```json
{
    "metadata": {
        "job_name": "experiment_module_name",   // Written by scheduler
        "tag_name": "tag_value"                 
    },                                          
    "timestamp": "mongoDB_ISO_date",            // Written by scheduler
    "_id": "mongoDB_Object_id",                 // Created by DB driver
    "key": "value",
    "another_key": "another_value",             
    "different_key": {                          // If your returned dictionary contains another dictionary
        "dictionary_key": "dictionary_value"    
    }
}
```

> [!NOTE]
> This will collect all data stored on each of the nodes, not just a single experiment

### JSON to CSV conversion
In the directory `translators` the repository includes a small script written in Rust that can translate collected JSON data to CSV. Edit the respective functions to choose which data are included. The CSV file has the same name and is saved in the same directory as the JSON.

parameters:
 - first parameter is path to the JSON file
 - the second parameter indicates which parser to invoke. For list of available values see match statement in `main.rs` on line 38

Example: `cd translators && cargo run --release /path/to/file.json file_type`

> [!CAUTION]
> Not all fields from JSON are dumped into CSV

## Included experiment modules
All parameters are required unless stated otherwise

> [!IMPORTANT]
> For all non-utility modules, the specific parameters belong to runtime configuration. For utility modules, they have their own field.

### Device
Collects telemetry from the starlink dish using grpc protocol.

Module specific parameters:
- `None`

### IP
Collects current IPv4 and IPv6 address

Module specific parameters:
- `None`
- Recommended period: 15s (= once per starlink widow)

### Traceroute
Collects traceroute against a list of targets.

For each target, returns a `dict` where keys correspond to hop distance and values contain `address` and `rtt_ms` fields. Only single packet is sent per hop

Module specific parameters:
- `targets: list[str]`: List of targets against which to run traceroute. Each string can be any of the following types: `IPv4`, `IPv6`, `FQDN`. Mixing is allowed

### Ping
Collects ping against a list of targets

For each target returns an object with `rtt_ms` property. If the reply comes from a different host or the target is FQDN additionally contains `address` property specifying the IP address

Module specific parameters:
- `targets: list[str]`: List of targets agaisnt which to collect ping (rtt) data. Each string can be any of the following types: `IPv4`, `IPv6`, `FQDN`. Mixing is allowed

### Weather
Collects weather data locally - precipitation and cloud coverage.
This module uses MET weather API, please familirize yourself with their [TOS](https://developer.yr.no/doc/TermsOfService/) before using the module.
In case your region is not covered you will have to find a different provider and/or write a custom version.

Module specific parameters:
- `user_agent: str`: Must conform to MET Weather API requirements
- Starlink dish configuration: Location enabled. The script queries the dish for GPS coordinates during the setup call. After setup, location can be disabled.

> [!CAUTION]
> MET API has rate limits and requires a valid `user_agent`. Not following their guidelines can result in the inability to collect data

### Space Weather
Collects space weather data on [NOAA Scale](https://www.spaceweather.gov/noaa-scales-explanation).
Underlying metrics (e.g. proton flux, k-index) are historically available on [spaceweather.gov](https://spaceweather.gov)

Module specific parameters:
- `None`

### Install (utility)
Installs dependencies using pip. This module is synchronous. It returns only when the installation is done or failed.

Parameters:
- `modules: list[str]`: List of modules to install

### Reboot (utility)
Reboots starlink dish.

> [!CAUTION]
> If using IPv6 addresses for addressing experiment nodes, this may cause unreachability

### Stow (utility)
Commands the starlink dish to enter or exit the stow state.

Parameters:
- `stow: boolean`: True will cause the dish to enter the stow state. False will cause to exit the stow state.


## Writing your own experiment modules
If you want to collect different metrics that are not included, read below to find out how to extend the functionality.

### Specification
You need to include 2 methods: `setup(conf_s)` and `collect(conf_c)`

`conf_s` contains data passed through the `setup` variable and `conf_c` contains data passed through the `config` variable as described in the [variables](#variables) section

The `setup` method is designed to run one-time preparition that depends on some external factors. A good example might be getting location from the dish for weather collection, or any expensive calls that do not need to be called with each data collection. Should you need to pass it some parameters via a playbook, they will be part of the `conf_s` dictionary.
Returns `void`.

The `collect` method is called every collection cycle exactly once. Parameters that are needed for every collection should be passed through the `conf_c` dictionary.
This method returns either `dict` or `list[dict]` with collected data. Should collecting fail, returning `None` is fine. The list of dictionaries is mostly used when doing the same job against several targets, see `modules/ping.py` for example. The data is stored in the same key-value format.

If either `collect` or `setup` throws exception, the subprocess for this collection will crash. Does not affect the main runner or other collecting subprocesses.

> [!NOTE]
> The scheduler takes care of injecting timestamp into the collected data object

> [!WARNING]
> When returning `list[dict]` and a different tag in metadata is needed for each of the results in the list, you must add it yourself. The tag should be part of the `metadata` dictionary in the object itself and will survive as long as there is not a name conflict. See `ping` module for example

### Testing
For your convenience there is `pytest` testing framework already included. Create a test file in the `tests` directory that has tests against your experiment module.
You can test the module end-to-end by instancing `Scheduler` with the `schedule` method. In that case, pass it the `dbg=True` parameter, it will disable the database and print results to `stdout` instead.

```python
import scheduler

def test(capsys):
    scheduler.schedule(config: dictionary, dbg=True)
```

``config`` is a dictionary that contains variables listed [above](#variables)  

To run tests there is a simple shell script included called `test.sh`


## FAQ

The automation script fails on "Start docker compose"
> If the CPU is x86_64 make sure it supports AVX instruction
> In case most don't have AVX instruction, read the question below this one

Most or all experiment nodes don't have AVX instruction, can I not use this?
> Remember that old mongoDB version is EOL, you're doing this at your own risk. Containers are configured to only expose port on local interface (`127.0.0.1`). 
> If this acceptable you can do that with a few tweaks:
> 1. in `docker-compose` change mongodb image tag from `7.0.11-ubi8` to `4.4.21-ubi8`
> 2. in `db.py` remove the `timeseries` named argument for the database
> 3. in `collect_measurements` playbook change `item.type == 'timeseries'` to `item.type == 'collection'`
> 4. rebuild the docker image, export it and then re-run `setup_node` playbook to deploy those changes
> 5. the list is non-exhaustive as it was not fully tested with such old HW. You might run into other issues

I changed the files that are part of the runner image, how do I redeploy it?
> Build and export the image from docker. Then include `deploy_image` fragment in your playbook.
> This will restart all the runners with the new image
> 
> WARNING: running experiments are in-memory only. You need to start them yourself again subsequently in the playbook

