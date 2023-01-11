import sys

if __name__ == "__main__":
    print("This is a supporting module. Do not execute directly.")
    sys.exit()

import json
from tkinter import messagebox
from error_handler import ErrorHandler

class JsonHandler:
    def __init__(self):
        self.ErrorHandler = ErrorHandler()

        # Message data to user if config file error
        self.reset_config_title = "Config file error"
        self.reset_config_msg = "Config file is missing or corrupt.\n\n" \
                                "Would you like to reset configuration to default values?\n\n" \
                                "(If you choose yes, CMN Splitter will run with its default settings. If you choose No, CMN Splitter will exit. You must either reset to default values or contact the software developer to resolve this.)"

    # Imports JSON file from file argument
    # default_cfg is the default configuration that can be used if the user wants to overwrite or
    # if user needs to use default because original config file is corrupt/missing.
    def import_json(self, file_name, default_cfg):
        self.file_name = file_name
        try: # Tries to read config file
            with open(self.file_name, "r") as config_file:
                self.config_options = json.load(config_file)
        except Exception as config_load_err: # If any errors occur (likely corrupt or missing)
            # Logs error, informs user
            # Will only return if user wants to reset to default config. Otherwise exits.
            self.config_error("Iniital config file load", caught_exc = config_load_err)

            # Writes out default config file as JSON
            self.write_default_cfg(default_cfg)

        # If length of config file differs from default config length in main.py
        # File is corrupt and must be replaced
        if len(self.config_options) != default_cfg["config_len"]:
            # Logs error, informs user.
            # Will only return if user wants to reset to default config;
            # otherwise exits within config_error().
            self.config_error("Incorrect config length")

            # Writes out default config file as JSON
            self.write_default_cfg(default_cfg)

        return self.config_options

    # Writes out provided default configuration (from main.py) to config file
    def write_default_cfg(self, default_cfg):
        self.config_options = default_cfg
        self.write_json(self.file_name, self.config_options)

    # Anytime an error occurs with configuration file
    # Logs error, informs user
    # User has the choice to reset to defaults or exit out
    def config_error(self, err_log_txt, caught_exc = None):
        self.ErrorHandler.log_err(err_log_txt, caught_exc)
        reset_config = messagebox.askyesno(
            title = self.reset_config_title,
            message = self.reset_config_msg
        )
        if reset_config == False:
            self.ErrorHandler.write_errs()
            sys.exit()

    # Writes the provided dictionary out to the config JSON file
    def write_json(self, file_name, config):
        self.file_name = file_name
        try: # Tries to write out the file
            with open(self.file_name, "w") as config_file:
                json.dump(config, config_file, indent = 4)

        # If errors, tells user
        # There is no built-in way to handle this. This would likely be due to a permission error.
        except Exception as write_json_err:
            self.ErrorHandler.log_err("Writing out config file", write_json_err)
            messagebox.showerror(
                title = "Error writing config file",
                message = "Error encountered writing config file.\n\n"
                          "Does CMN Splitter have insufficient permissions to write?\n"
                          "Is the config file open in another program (or another instance of CMN Splitter)?\n\n"
                          "If this error persists, contact the software developer."
            )

        # Sets software's configuration to newly set options if export is successful
        else: self.config_options = config