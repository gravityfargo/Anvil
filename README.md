1. Create a project with `./anvil_cli.py createproject <project_name>` \
or import an existing project with `./anvil_cli.py importproject <project_name>`



Minimum:
- in the repo folder, clone an empy git repository.
- in its folder, create a `ansible_hosts` file in yml format
    - hosts must only belong to one group (for now)
    - parent directories are made based on the groups and the hosts

```shell
./anvil_cli.py createproject <project_name>
# or
./anvil_cli.py importproject <project_name>


./anvil_cli.py createhost <host_name>

# ./anvil_cli.py -l projects
./anvil_cli.py -l groups
./anvil_cli.py -g <group_name> -l hosts

```