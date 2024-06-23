#!/usr/bin/env python
import sys
from config.vars import AnvilData
from core.anvil_gui import anvil_gui
from core.anvil_cli import anvil_cli

if __name__ == "__main__":
    ad = AnvilData()
    ad.initialize()

    if len(sys.argv) > 1:
        anvil_cli(ad)
    else:
        anvil_gui(ad)
