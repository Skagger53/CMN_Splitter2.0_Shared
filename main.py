# CMN Splitter
# Case Mix Notice Splitter
# A program by Matt Skaggs
# Proprietary license. Redistribution outside of Monarch Healthcare is strictly prohibited.


# ------------------ OVERVIEW ------------------
# 1. Imports config file (json_handler.py). Deals with any errors (corrupt file, etc.)
# 2. Launches main window (tkinter_handler.py). Only two buttons for user.
# 3. User can click "Select Case Mix Notice" button (pdf_handler.py) or "Exit"
# 4. Case Mix Notice is selected, validated, split up, and exported (pdf_handler.py) using config file settings
# 5. User can split multiple files in a row if desired
# At any time, user can use keyboard shortcut Ctrl+Shift+O
# to reach configuration options (within tkinter_handler.py).
#   User can change syntax of file name; default export and import directories; etc.
#   Changes are saved to the config file.


import sys

if __name__ != "__main__":
    print("This is the main module. Do not call.")
    sys.exit()

import json
from tkinter_handler import MainWindow
from json_handler import JsonHandler
from hardcoded_config import default_cfg

# Handles importing and exporting settings to cfg (JSON format)
JsonHandler = JsonHandler()

# Config file name is only specified here
file_name = "cmn.cfg"

# Imports configuration file
# If errors found, JsonHandler gives user option to reset config to defaults from hardcoded_config
config_options = JsonHandler.import_json(
  file_name,
  default_cfg
)

main_win = MainWindow(file_name, config_options)