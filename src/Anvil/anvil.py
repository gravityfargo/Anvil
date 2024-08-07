#!/usr/bin/env python
from Anvil.classes import AnvilData
from Anvil.gui import anvil_gui


if __name__ == "__main__":
    ad = AnvilData()
    # if len(sys.argv) > 1:
    #     # anvil_cli(ad)
    #     pass
    # else:
    anvil_gui(ad)
