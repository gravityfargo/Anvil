from ansible_runner import *
from os import path, getcwd
from cli.file_utils import YamlManager
from config.vars import ANVIL_DATA_FILE


def ping(hosts_file, host_name):
    rc = RunnerConfig(
        private_data_dir="project",
        inventory=path.join(getcwd(), hosts_file),
        module="ping",
        host_pattern=host_name,
    )
    rc.prepare()
    r = Runner(config=rc)
    r.run()


# r = ansible_runner.run(
#     inventory='inventory.yml',
#     playbook='playbook.yml',
#     host_pattern='all',
#     extravars={
#         'ansible_user': 'user',
#         'ansible_password': 'password'
#     }
# )


def demo():
    # get list of changed ansible configuration values
    out, err = get_ansible_config(
        action="dump", config_file="/home/demo/ansible.cfg", only_changed=True
    )
    print("out: {}".format(out))
    print("err: {}".format(err))


demo()
