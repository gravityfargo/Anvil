import click
from anvil.config import init
from anvil.gui import gui_main

init()


@click.group(
    help="Anvil is a tool for managing and interacting with remote hosts using Ansible."
)
def anvil():
    pass


anvil.add_command(gui_main)
