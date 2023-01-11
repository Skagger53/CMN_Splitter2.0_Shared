import os.path
import sys

if __name__ == "__main__":
    print("This is a supporting module. Do not execute directly.")
    sys.exit()

# AT THE END OF SPLITTING, RESET VALUES AS NEEDED IN CASE USER WANTS TO SPLIT ANOTHER FILE
# AVOID OVERWRITING

import PyPDF2
import datetime
from tkinter import filedialog, messagebox
from pathlib import Path
from error_handler import ErrorHandler

class PdfHandler:
    def __init__(self):
        # Creates error handler
        self.ErrorHandler = ErrorHandler()

        self.corrupt_file_msg = "Selected file could not be imported.\n\nFile may be corrupt."
        self.page_num_msg = "Selected file failed validation (page count).\n\nPlease choose a valid Case Mix Notice file."
        self.no_txt_msg = "Selected file failed validation (no text found).\n\nPlease choose a valid Case Mix Notice file."
        self.txt_valid_msg = "Selected file failed validation (page 1 text evaluation).\n\nPlease choose a valid Case Mix Notice file."
        self.set_syntax_msg = "Selected file failed to process (setting file name syntax).\n\n" \
                              "Please ensure the Case Mix file is not corrupt and the configuration file is not corrupt"
        self.set_final_syntaxt_list_msg = \
            "Selected file failed to process (final file name syntax list).\n\n" \
            "Please ensure the Case Mix file is not corrupt and the configuration file is not corrupt"
        self.final_page_count_msg = "Selected file failed to process (final page count).\n\n" \
                                    "Please ensure you have selected a valid Case Mix Notice file and that the file is not corrupt."
        self.invalid_odir_msg = "Default export directory is invalid. This setting will be reset."
        self.failed_export_msg = "Failed to write PDF.\n\nPlease ensure the directory you selected is still available and is not write-protected."
        # These next two error messages are unique, since they need to be broken up to notify user of specific failed data extraction
        # Used in self.evaluate_contents() and self.create_raw_filename_list()
        self.page_0_extract_msg = ("Selected file failed validation (page 1 data detection", "Please choose a valid Case Mix Notice file.")
        self.extract_msg = ("Data extraction failed (page ", "Please ensure the Case Mix file is not corrupt and the configuration file is not corrupt.")

    # Imports PDF.
    # Returns two-element tuple: ({bool for successful/failed import}, {bool for reset import pdf setting due to invalid dir})
    def import_pdf(self, config_options):
        input_dir = config_options["inp_def_dir"]
        reset_dir = False
        if input_dir != "": # If there is an input directory in configuration file
            if not os.path.isdir(input_dir): # Tests if directory is valid
                messagebox.showerror(
                    title = "Invalid default directory",
                    message = "Default input directory in configuration file is invalid. This setting will be reset."
                )
                reset_dir = True
                input_dir = ""

        self.file_name = filedialog.askopenfilename(
            title = "Select Case Mix Notice file",
            initialdir = input_dir,
            filetypes = [("PDF files", "*.pdf")]
        )
        if self.file_name == "": return (False, reset_dir) # Did not get import directory from user
        return (True, reset_dir)

    # Evaluates contents to validate that this is a Case Mix Notice file
    def evaluate_contents(self, config_options):
        with open(self.file_name, "rb") as cm_file:
            # Resets variables in case import process is interrupted/fails so "normal" reassignment fails
            self.num_pages = None
            self.file_name_list_raw = []
            self.file_name_list_final = []

            self.date_format = config_options["extraction_settings"]["date_format"]
            self.name_prec_text = config_options["extraction_settings"]["name_date_extract"][0]
            self.date_prec_text = config_options["extraction_settings"]["name_date_extract"][1]
            self.name_char_count = config_options["extraction_settings"]["name_date_extract"][2]
            self.date_char_count = config_options["extraction_settings"]["name_date_extract"][3]
            self.code_succ_text = config_options["extraction_settings"]["name_date_extract"][4] # Text ele succeeding code
            self.code_list = config_options["extraction_settings"]["code_list"]

            # Imports PDF file, catching possible errors
            try: pdf_obj = PyPDF2.PdfReader(cm_file)
            except Exception as read_pdf_e:
                self.ErrorHandler.log_err("Called PyPDF2.PdfReader()", read_pdf_e)
                return self.corrupt_file_msg

            # Checks that file has an even number of pages
            self.num_pages = pdf_obj.getNumPages()
            if self.num_pages % 2 != 0:
                return self.page_num_msg

            # Evaluates page 0's text
            test_txt = pdf_obj.getPage(0).extractText()

            if test_txt == "": # If page 1 has no text
                return self.no_txt_msg

            test_txt = test_txt.split("\n") # Splits page 1 text by line breaks

            # Checks file's text against config file's validation information
            # first list element = index of imported page 0 text broken up by new line (meaning page 0, line X)
            # second list element = text that first element should contain
            if test_txt[config_options["file_valid1"][0]] != config_options["file_valid1"][1] or \
               test_txt[config_options["file_valid2"][0]] != config_options["file_valid2"][1]:
                return self.txt_valid_msg

            # Checks that needed data can be found in test page (page 0)
            test_page_0 = self.extract_data(test_txt)
            if test_page_0[0] == False:
                """Example error message:
                
                   Selected file failed validation (page 1 data detection, date)
                   Please choose a valid Case Mix Notice file."""
                return f"" \
                       f"{self.page_0_extract_msg[0]}, {test_page_0[1]}).\n\n" \
                       f"{self.page_0_extract_msg[1]}"

    # Creates exporting file names list. List of tuples.
    # This is "raw", i.e., always in the order of ({name}, {date}, {code})
    # self.create_filenames arranges list into proper syntax from config file
    def create_raw_filename_list(self):
        with open(self.file_name, "rb") as cm_file:
            pdf_obj = PyPDF2.PdfReader(cm_file)
            for i in range(0, self.num_pages, 2): # Only odd pages
                next_data_set = self.extract_data(pdf_obj.getPage(i).extractText().split("\n")) # Splits full text on line breaks
                if next_data_set[0] == False:
                    """Example error message:
                       Data extraction failed (page 2, code).
                       Please ensure the Case Mix file is not corrupt and the configuration file is not corrupt."""
                    return f"" \
                           f"{self.extract_msg[0]}{i + 1}, {next_data_set[1]}).\n\n" \
                           f"{self.extract_msg[1]}"
                self.file_name_list_raw.append(next_data_set)

    # Attempts to extract name from provided line of text
    # txt_split is a page's text already split by line breaks
    # Successful validation returns 3-ele tuple: ({name}, {date}, {code})
    # Failure to validate returns 2-ele tuple: (False, {str term for failed data extraction})
    def extract_data(self, txt_split: str):
        name = self.extract_name(txt_split)
        if name == False: return (False, "name")

        date = self.extract_date(txt_split)
        if date == False: return (False, "date")

        code = self.extract_code(txt_split)
        if code == False: return (False, "code")

        return (name, date, code)

    # Attempts to extract code from provided page text
    # Matches text in element succeeding code
    # Success returns string of code
    # Failure lots error and returns False
    def extract_code(self, text):
        code = ""
        try:
            for i in range(len(text)):
                if text[i].strip()[:len(self.code_succ_text)] == self.code_succ_text:
                    code = text[i - 1][-3:].strip() # Only takes final 3 characters from element with code
                    break
        except Exception as code_e:
            self.ErrorHandler.log_err(f"Attempted to extract code from {text}", code_e)
            return False
        else:
            if code == "": # No code found/assigned
                self.ErrorHandler.log_err(f"Failed to find code in {text}", None)
                return False
            if code in self.code_list: return code # Ensures code extracted is in list of actual codes
            self.ErrorHandler.log_err(f"Retrieved {code} as Case Mix", None)
            return False

    # Attempts to extract date from provided list of text
    # Matches text immediately preceding the date
    # Success returns string of date
    # Failure lots error and returns False
    def extract_date(self, text):
        date = ""
        try:
            for i in range(len(text)):
                if text[i].strip()[:len(self.date_prec_text)] == self.date_prec_text: # Matches text immediately preceding date
                    # Begins after text preceding date and only goes until the end of the date text (should be 10 chars)
                    date = text[i][
                           len(self.date_prec_text) : len(self.date_prec_text) + abs(self.date_char_count)
                           ].strip()
                    date = datetime.datetime.strptime(date, self.date_format)
                    break
        except Exception as date_e:
            self.ErrorHandler.log_err(f"Attempted to extract date from {text}", date_e)
            return False
        else:
            if date == "": # No date value found/assigned
                self.ErrorHandler.log_err(f"Failed to extract date from {text}", None)
                return False
            return date.strftime("%m.%d.%Y")

    # Attempts to extract name from provided list of text
    # Matches text in list element immediately preceding name
    # Success returns string of name
    # Failure logs error and returns False
    def extract_name(self, text):
        name = ""
        try:
            for i in range(len(text)):
                if self.name_prec_text == text[i].strip():
                    # self.name_char_count offsets by proper number of characters to not include end of line date
                    name = text[i + 1][:self.name_char_count]\
                        .title()\
                        .strip()\
                        .replace(" ", "")
        except Exception as name_e:
            self.ErrorHandler.log_err(f"Attempted to extract patient name from {text}", name_e)
            return False
        else:
            if name == "": # No name found/assigned
                self.ErrorHandler.log_err(f"Failed to find name from {text}", None)
                return False
            return name

    def divide_export_pdf(self):
        pass

    def create_filenames(self, config_options):
        syntax = []

        # Sets proper syntax for all exports based on configuration file
        # Raw file name order is ({name}, {date}, {code})
        try:
            for i in range(0, 3): # Based on config file, sets up order of indices to use below when creating file names
                if config_options["syntax"][str(i)].lower() == "patient name": syntax.append(0)
                if config_options["syntax"][str(i)].lower() == "effective date": syntax.append(1)
                if config_options["syntax"][str(i)].lower() == "case mix": syntax.append(2)
        except Exception as set_syntax_e:
            self.ErrorHandler.log_err("Attempted to set file name syntax", set_syntax_e)
            return self.set_syntax_msg
        try:
            for i in range(len(self.file_name_list_raw)): # Follows indices found in syntax to create file name order list
                self.file_name_list_final.append(
                    (
                        self.file_name_list_raw[i][syntax[0]],
                        self.file_name_list_raw[i][syntax[1]],
                        self.file_name_list_raw[i][syntax[2]]
                    )
                )
        except Exception as set_final_syntax_e:
            self.ErrorHandler.log_err("Attempted to create final file name syntax list", set_final_syntax_e)
            return self.set_final_syntaxt_list_msg

        # Prepending settings
        prep_num = config_options["prepending"]["prepend_num"]
        if prep_num == 0: prep_num = ""
        prep_txt = config_options["prepending"]["prepend_txt"]

        for i in range(len(self.file_name_list_final)):
            # Sets up file name. Checks for various prepending preferences and properly enters terms, sets spacing
            if prep_num == 1 and prep_txt != "": file_name = f"CM{i + 1:03d} {prep_txt} "
            elif prep_num == 1: file_name = f"CM{i + 1:03d} "
            elif prep_txt != "": file_name = prep_txt + " "
            else: file_name = ""

            # Each file name is the prepending text from above and then the proper order from the config file of patient data
            self.file_name_list_final[i] = f"{file_name}{self.file_name_list_final[i][0]}_{self.file_name_list_final[i][1]}_{self.file_name_list_final[i][2]}"

    # Exports PDFs
    # Uses default directory if one is set; otherwise prompts user for directory
    # Returns two- or three-element tuple
        # ({bool for successful or failed export}, {bool for resetting export director due to invalid directory},
        # {error str message to user if element 1 was True})
    def export_pdfs(self, config_options):
       # Auto-generated folder name
       # This is only used if config file does not have a custom folder name or
       # if the user's custom folder name already exists.
       folder_name = "Case Mix letters " +\
                     datetime.datetime.strftime(
                         datetime.datetime.now(),
                         "%Y%m%d%H%M%S"
                     )

       # Opens file to obtain contents to divide and export
       with open(self.file_name, "rb") as cm_file:
           reset_dir = False # Whether or not to reset export directory

           pdf_obj = PyPDF2.PdfReader(cm_file)
           num_pages = pdf_obj.getNumPages()

           # Checks that file length lines up with number of file names to use in export
           if num_pages % 2 != 0 or num_pages / 2 != len(self.file_name_list_final):
               return (self.final_page_count_msg, reset_dir)

           # Obtains and validates output directory
           output_dir = config_options["exp_def_dir"]
           if output_dir != "" and not os.path.isdir(output_dir): # Custom dir in config file but invalid
               messagebox.showerror(
                   title = "Invalid output directory",
                   message = self.invalid_odir_msg
               )
               reset_dir = True # Default output dir needs to be reset to nothing
               output_dir = ""
           if output_dir == "": # No custom dir in config file
               messagebox.showinfo(
                   title = "Select directory",
                   message = "Please choose where to save letters."
               )
               output_dir = filedialog.askdirectory(initialdir = self.file_name[:self.file_name.rfind("/")])
               if output_dir == "": return (False, reset_dir, False)

           custom_folder = config_options["exp_folder"]
           if custom_folder != "": # Config file has custom export folder name
               if os.path.isdir(output_dir + "/" + custom_folder): # Custom directory already exists (and may have exported PDFs inside it)
                   messagebox.showerror(
                       title = "Export folder already exists",
                       message = "Your default export folder name already exists. A new folder name will be auto-generated for this export."
                   )

               else: folder_name = custom_folder

           # Creates output folder
           output_dir = output_dir + "/" + folder_name
           os.makedirs(output_dir)
           output_dir = output_dir + "/"

           # Loops through all file names and exports PDF pages with the name
           for i in range(len(self.file_name_list_final)):
               pdf_writer = PyPDF2.PdfWriter()
               pdf_writer.addPage(pdf_obj.getPage(i * 2))
               pdf_writer.addPage(pdf_obj.getPage(i * 2 + 1))

               # Creates appendation if file already exists (two letters to same person with
               # identical extracted details)
               if os.path.isfile(output_dir + self.file_name_list_final[i] + ".pdf"): append = "_2"
               else: append = ""

               # Attempts to write out PDF. If this fails, it's likely due to a permission error, since
               # PDF contents and directory have already been validated. Another possibility is if the user
               # has entered a custom file or folder name with an invalid character.
               try:
                   with Path(output_dir + self.file_name_list_final[i] + append + ".pdf").open(mode = "wb") as output_pdf:
                       pdf_writer.write(output_pdf)
               except Exception as write_pdf_e:
                   self.ErrorHandler.log_err(f"Attempted to write out PDF pages {i * 2} to {i * 2 + 1}", write_pdf_e)
                   return (False, reset_dir, self.failed_export_msg)

           return(True, reset_dir, output_dir)