import sys

if __name__ == "__main__":
    print("This is a supporting module. Do not execute directly.")
    sys.exit()

import datetime
import csv
import os

class ErrorHandler:
    def __init__(self):
        self.current_log = []

    # action_descr is a text description of what happened
    # exception is the Exception logged by Python
    # PERMIT None TO BE EXCEPTION
    def log_err(self, action_descr, exception):
        self.current_log.append(
            (
                action_descr,
                exception,
                datetime.datetime.strftime(
                    datetime.datetime.now(),
                    "%Y.%m%d %H%M"
                )
            )
        )

    # Writes out errors to error log file
    def write_errs(self, log_filename: str, log_length: int):
        if len(self.current_log) == 0: return # Writes nothing if there are no errors
        if not os.path.exists(log_filename): # There is no existing error log
            # Creates new error log with current errors
            with open(log_filename, "w") as error_log_file:
                csv_writer = csv.writer(error_log_file)
                csv_writer.writerows(self.current_log)
            return

        # An error log already exists
        with open(log_filename, "r") as loaded_log_file:
            current_log = csv.reader(loaded_log_file)

            # Turns into list excluding empty lines
            current_log = [row for row in current_log if len(row) != 0]
            # Adds current errors
            for row in self.current_log: current_log.append(row)

        # Limits error log length to config file's settings
        if len(current_log) > log_length: current_log = current_log[-log_length:]
        # Writes out new log
        with open(log_filename, "w") as new_log_file:
            new_log = csv.writer(new_log_file)
            new_log.writerows(current_log)