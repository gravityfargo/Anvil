#!/usr/bin/env python
import sys
from core.classes import AnvilData, Printer
from core.anvil_gui import anvil_gui

# from core.anvil_cli import anvil_cli


if __name__ == "__main__":
    ad = AnvilData()
    p = Printer("class", "Anvil")
    p.vfunc = "__main__()"

    if len(sys.argv) > 1:
        p.route = "cli"
        p.info("CLI Mode")
        # anvil_cli(ad)
    else:
        p.route = "gui"
        p.info("GUI Mode")
        anvil_gui(ad)
