import sys

if __name__ == "__main__":
    print("This is a supporting module. Do not execute directly.")
    sys.exit()

import os
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as filedialog
from tkinter import END # Used for clearing entry widgets
from PIL import Image, ImageTk
from json_handler import JsonHandler
from pdf_handler import PdfHandler

class MainWindow:
    def __init__(self, file_name, config_options):
        self.file_name = file_name

        # Creates a copy of config_options to use in self.save_exit_config
        # Can't pass arguments to self.save_exit_config due to using keyboard shortcut
        self.config_options = config_options

        self.window_x = config_options["window_size"]["window_x"]
        self.window_y = config_options["window_size"]["window_y"]
        self.window_title = config_options["window_title"]

        self.exp_folder = config_options["exp_folder"]
        self.prepending = config_options["prepending"]
        self.syntax = config_options["syntax"]
        self.exp_def_dir = config_options["exp_def_dir"]
        self.inp_def_dir = config_options["inp_def_dir"]

        # Main window elements/elements layout
        self.logo_full_file = "logo2.jpg"
        self.logo_ico_file = "logo1.ico"

        # The self.resource_path() method is only needed for compiling CMN Splitter into a single-file executable;
        # without it the application crashes.
        # The method has no adverse effects when used even when not needed (e.g., run through an IDE).
        self.logo_full_file = self.resource_path(self.logo_full_file)
        self.logo_ico_file = self.resource_path(self.logo_ico_file)

        self.browse_pady = (2, 8)

        # Config window frame outlines
        self.conf_frame_settings = {
            "highlightbackground": "gray",
            "highlightthickness": 1,
            "padx": 5,
            "pady": 5
        }

        # Config window size
        self.config_window_x = 840
        self.config_window_y = 310

        # Config widget pad settings
        self.config_widget_padx = 12
        self.config_widget_pady = 6

        # Config directory selection button width
        self.config_dir_button_width = 17

        # Config syntax drop-down width
        self.config_namesyntax_option_width = 12

        # Config window first frame start row
        self.config_first_row = 1

        # Setting options for file name syntax (used in drop-down menus in config window)
        self.config_syntax_opt_setup()

        # List of invalid characters for file names (used in validating config input)
        self.invalid_chars = self.config_options["invalid_chars"]

        # Length of Entry widget for directories
        self.dir_entry_len = 70

        self.json_handler = JsonHandler()
        self.pdf_handler = PdfHandler()

        self.create_main_win()

    def create_main_win(self):
        self.main_win = tk.Tk()

        # Per config file, creates window at specified size and sets it in center of screen or not
        if self.config_options["center_window"] == 1:
            self.screen_size = (
                self.main_win.winfo_screenwidth(),
                self.main_win.winfo_screenheight()
            )
            self.window_loc_x = self.screen_size[0]/2 - self.window_x/2
            self.window_loc_y = self.screen_size[1]/2 - self.window_y/2
        else:
            self.window_loc_x = 0
            self.window_loc_y = 0

        self.main_win.title(self.window_title)
        # Creates window and sets it in center of screen per config (or offsets by 0)
        self.main_win.geometry(
            f"{self.window_x}x{self.window_y}+"
            f"{int(self.window_loc_x)}+{int(self.window_loc_y)}"
        )
        self.main_win.resizable(False, False)
        self.main_win.configure(bg = "#F0F0F0")

        # Window icon
        logo_ico = Image.open(self.logo_ico_file)
        logo_ico = ImageTk.PhotoImage(logo_ico)

        self.main_win.wm_iconphoto(True, logo_ico)

        # Main logo
        logo_full = Image.open(self.logo_full_file)
        logo_full = ImageTk.PhotoImage(logo_full)

        self.logo_label = tk.Label(image = logo_full)
        self.logo_label.grid(row = 0, column = 0)

        # Browse button
        self.browse_btn = tk.Button(
            self.main_win,
            text = "I\u0332mport Notice File",
            command = self.import_pdf
        )
        self.browse_btn.grid(row = 1, column = 0, pady = self.browse_pady)
        self.main_win.bind("<Alt-i>", self.import_pdf)

        # Exit button with keyboard shortcut
        self.exit_btn = tk.Button(self.main_win, text = "Ex\u0332it", command = self.exit_main_win)
        self.exit_btn.grid(row = 2, column = 0)
        self.main_win.bind("<Alt-x>", self.exit_main_win)

        # Keyboard shortcut for opening configuration options
        self.main_win.bind("<Control-O>", self.create_config_win)

        # Catches when user clicks window's X button
        self.main_win.protocol("WM_DELETE_WINDOW", self.exit_main_win)

        self.main_win.focus_force()
        self.main_win.mainloop()

    # Simple exit
    def exit_main_win(self, e = None):
        if messagebox.askyesno(
                title = "Close",
                message = "Do you want to exit?"
        ):
            # Writes out any errors
            self.pdf_handler.ErrorHandler.write_errs(
                self.config_options["err_log"]["file_name"],
                self.config_options["err_log"]["err_log_len"]
            )
            self.main_win.destroy()
            sys.exit()

    # Creates the configuration window. Hides main window.
    def create_config_win(self, e = None):
        self.main_win.withdraw() # Hiding main window

        # New directories as chosen by user
        # Outputted to config file when user saves
        self.new_dirs = {
            "new_inp_dir": "",
            "new_out_dir": ""
        }

        self.config_win = tk.Tk()

        # Per config file, centers window or offsets by 0
        if self.config_options["center_window"] == 1:
            self.c_window_loc_x = self.screen_size[0] / 2 - self.config_window_x / 2
            self.c_window_loc_y = self.screen_size[1] / 2 - self.config_window_y / 2
        else:
            self.c_window_loc_x = 0
            self.c_window_loc_y = 0

        self.config_win.geometry(
            f"{self.config_window_x}x{self.config_window_y}+"
            f"{int(self.c_window_loc_x)}+{int(self.c_window_loc_y)}"
        )
        self.config_win.title("Configuration")

        # Frame for all settings
        self.conf_full_frame = tk.Frame(self.config_win)
        self.conf_full_frame.grid(row = 0, column = 0)

        # ----------- Directory setting -----------
        self.conf_dir_frame = tk.Frame(
            self.conf_full_frame,
            highlightbackground = self.conf_frame_settings["highlightbackground"],
            highlightthickness = self.conf_frame_settings["highlightthickness"]
        )
        self.conf_dir_frame.grid(
            row = self.config_first_row,
            column = 0,
            padx = self.conf_frame_settings["padx"],
            pady = self.conf_frame_settings["pady"],
            sticky = "w"
        )

        # Default export folder name
        self.conf_exp_name_label = tk.Label(
            self.conf_dir_frame,
            text = "Default export folder name (blank for auto-generated name):"
        )
        self.conf_exp_name_label.grid(
            row = 0,
            column = 0,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady,
            sticky = "e"
        )

        self.conf_exp_name_entry = tk.Entry(self.conf_dir_frame, width = 30)
        self.conf_exp_name_entry.insert(0, self.config_options["exp_folder"])
        self.conf_exp_name_entry.grid(
            row = 0,
            column = 1,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        # ----------- Default input and output directories -----------
        self.conf_dir_frame = tk.Frame(
            self.conf_full_frame,
            highlightbackground = self.conf_frame_settings["highlightbackground"],
            highlightthickness = self.conf_frame_settings["highlightthickness"]
        )
        self.conf_dir_frame.grid(
            row = self.config_first_row + 1,
            column = 0,
            padx = self.conf_frame_settings["padx"],
            pady = self.conf_frame_settings["pady"]
        )

        # Setting input directory
        self.conf_idir_label = tk.Label(
            self.conf_dir_frame,
            text = "Default input directory:"
        )
        self.conf_idir_label.grid(
            row = 0,
            column = 0,
            sticky = "e",
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        self.conf_idir_entry = tk.Entry(self.conf_dir_frame, width = self.dir_entry_len)
        self.conf_idir_entry.grid(
            row = 0,
            column = 1,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )
        self.conf_idir_entry.insert(0, self.config_options["inp_def_dir"])
        self.conf_idir_entry["state"] = "disabled"

        self.conf_idir_btn = tk.Button(
            self.conf_dir_frame,
            text = "Select input directory",
            width = self.config_dir_button_width,
            command = lambda: self.get_dir(
                False,
                "new_inp_dir",
                self.conf_idir_entry
            )
        )
        self.conf_idir_btn.grid(
            row = 0,
            column = 2,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        self.conf_idir_reset_btn = tk.Button(
            self.conf_dir_frame,
            text = "Reset",
            command = lambda: self.get_dir(True, "new_inp_dir", self.conf_idir_entry)
        )
        self.conf_idir_reset_btn.grid(
            row = 0,
            column = 3,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        # Setting output directory
        self.conf_odir_label = tk.Label(
            self.conf_dir_frame,
            text = "Default output directory:"
        )
        self.conf_odir_label.grid(
            row = 1,
            column = 0,
            sticky = "e",
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        self.conf_odir_entry = tk.Entry(self.conf_dir_frame, width = self.dir_entry_len)
        self.conf_odir_entry.grid(
            row = 1,
            column = 1,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )
        self.conf_odir_entry.insert(0, self.config_options["exp_def_dir"])
        self.conf_odir_entry["state"] = "disabled"

        self.conf_odir_btn = tk.Button(
            self.conf_dir_frame,
            text = "Select output directory",
            width = self.config_dir_button_width,
            command = lambda: self.get_dir(
                False,
                "new_out_dir",
                self.conf_odir_entry
            )
        )
        self.conf_odir_btn.grid(
            row = 1,
            column = 2,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        self.conf_odir_reset_btn = tk.Button(
            self.conf_dir_frame,
            text = "Reset",
            command = lambda: self.get_dir(True, "new_out_dir", self.conf_odir_entry)
        )
        self.conf_odir_reset_btn.grid(row = 1, column = 3)

        # ----------- Prepending files -----------
        self.conf_prep_frame = tk.Frame(
            self.conf_full_frame,
            highlightbackground = self.conf_frame_settings["highlightbackground"],
            highlightthickness = self.conf_frame_settings["highlightthickness"]
        )
        self.conf_prep_frame.grid(
            row = self.config_first_row + 2,
            column = 0,
            padx = self.conf_frame_settings["padx"],
            pady = self.conf_frame_settings["pady"],
            sticky = "w"
        )

        # Prepend with custom text
        self.conf_preptxt_label = tk.Label(
            self.conf_prep_frame,
            text = "Custom file name prepend text:",
            width = 30,
            anchor = "e"
        )
        self.conf_preptxt_label.grid(
            row = 0,
            column = 0,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        self.conf_preptxt_entry = tk.Entry(self.conf_prep_frame)
        self.conf_preptxt_entry.grid(
            row = 0,
            column = 1,
            sticky = "w",
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )
        self.conf_preptxt_entry.insert(0, self.config_options["prepending"]["prepend_txt"])

        # Enable/disable generated number prepend
        self.conf_prepnum_label = tk.Label(
            self.conf_prep_frame,
            text = "Prepend file name's with generated number?"
        )
        self.conf_prepnum_label.grid(
            row = 1,
            column = 0,
            sticky = "e",
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        self.conf_prepnum_intvar = tk.IntVar(self.config_win)
        self.conf_prepnum_chk = tk.Checkbutton(
            self.conf_prep_frame,
            variable = self.conf_prepnum_intvar,
            onvalue = 1,
            offvalue = 0
        )
        self.conf_prepnum_chk.grid(
            row = 1,
            column = 1,
            sticky = "w",
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )
        if self.config_options["prepending"]["prepend_num"] == 1: self.conf_prepnum_chk.select()

        # ----------- File name syntax -----------
        self.conf_namesyntax_frame = tk.Frame(
            self.conf_full_frame,
            highlightbackground = self.conf_frame_settings["highlightbackground"],
            highlightthickness = self.conf_frame_settings["highlightthickness"]
        )
        self.conf_namesyntax_frame.grid(
            row = self.config_first_row + 4,
            column = 0,
            padx = self.conf_frame_settings["padx"],
            pady = self.conf_frame_settings["pady"],
            sticky = "w"
        )

        # Label for file name syntax
        self.conf_namesyntax_label = tk.Label(self.conf_namesyntax_frame, text = "File name syntax:")
        self.conf_namesyntax_label.grid(
            row = 0,
            column = 0,
            padx = self.config_widget_padx,
            pady = self.config_widget_pady
        )

        # Setting up all StringVars for file name syntax drop-down menus
        # Setting default values for file name syntax based on loaded config settings
        self.conf_namesyntax_optmenu1_SV = tk.StringVar(self.config_win)
        self.conf_namesyntax_optmenu1_SV.set(self.config_syntax_opt[0])
        self.conf_namesyntax_optmenu2_SV = tk.StringVar(self.config_win)
        self.conf_namesyntax_optmenu2_SV.set(self.config_syntax_opt[1])
        self.conf_namesyntax_optmenu3_SV = tk.StringVar(self.config_win)
        self.conf_namesyntax_optmenu3_SV.set(self.config_syntax_opt[2])

        # All three drop-downs one after the other
        self.conf_namesyntax_optmenu1 = tk.OptionMenu(
            self.conf_namesyntax_frame,
            self.conf_namesyntax_optmenu1_SV,
            *self.config_syntax_opt

        )
        self.conf_namesyntax_optmenu1.config(width = self.config_namesyntax_option_width)
        self.conf_namesyntax_optmenu1.grid(row = 0, column = 1)

        self.conf_namesyntax_optmenu2 = tk.OptionMenu(
            self.conf_namesyntax_frame,
            self.conf_namesyntax_optmenu2_SV,
            *self.config_syntax_opt
        )
        self.conf_namesyntax_optmenu2.config(width=self.config_namesyntax_option_width)
        self.conf_namesyntax_optmenu2.grid(row = 0, column = 2)

        self.conf_namesyntax_optmenu3 = tk.OptionMenu(
            self.conf_namesyntax_frame,
            self.conf_namesyntax_optmenu3_SV,
            *self.config_syntax_opt
        )
        self.conf_namesyntax_optmenu3.config(width=self.config_namesyntax_option_width)
        self.conf_namesyntax_optmenu3.grid(row = 0, column = 3)

        # Save and exit button with keyboard shortcut
        self.config_save_btn = tk.Button(
            self.config_win,
            text = "Sav\u0332e and return",
            command = self.save_exit_config
        )
        self.config_save_btn.grid(
            row = self.config_first_row + 5,
            column = 0,
            pady = (15, 0)
        )
        self.config_win.bind("<Alt-v>", self.save_exit_config)

        # Catches when user clicks window's X button or uses hidden shortcut Alt-x
        self.config_win.bind("<Alt-x>", self.catch_c_win_close)
        self.config_win.protocol("WM_DELETE_WINDOW", self.catch_c_win_close)

        self.config_win.focus_force() # Brings OS window focus to config window
        self.config_win.mainloop()

    # Sets disabled Entry widget text and associated variable
    # If reset_dir == True, sets Entry text and associated variable to ""
    # If reset_dir == False, gets new directory from user
    # If user selected a new directory, puts that in the Entry widget
    def get_dir(self, reset_dir: bool, dir_var: str, entry_widget: tk.Entry):
        if reset_dir: selected_dir = ""
        else:
            selected_dir = filedialog.askdirectory()
            if selected_dir == "": return

        self.new_dirs[dir_var] = selected_dir
        self.update_entry(entry_widget, selected_dir)

    # Updates disabled entry widget text value
    def update_entry(self, entry_widget: tk.Entry, new_text: str):
        entry_widget["state"] = "normal"
        entry_widget.delete(0, END)
        entry_widget.insert(0, new_text)
        entry_widget["state"] = "disabled"

    # When user clicks the config window's X button
    def catch_c_win_close(self, e = None):
        if messagebox.askyesno(title="Save?", message="Do you want to save this configuration?"):
            # First validates user inputs.
            # If anything fails, user is informed in self.check_config_inputs() and the exit is canceled.
            if self.check_config_inputs() == False: return
            self.export_json()
        self.exit_config_win()

    # Validates config inputs
    # Informs user of any failed validation and returns False
    def check_config_inputs(self):
        # Obtaining user-provided text from widgets
        folder_name = self.conf_exp_name_entry.get()
        self.new_dirs["new_inp_dir"] = self.conf_idir_entry.get()
        self.new_dirs["new_out_dir"] = self.conf_odir_entry.get()
        prep_txt = self.conf_preptxt_entry.get()
        prep_gen_num = self.conf_prepnum_intvar.get()
        name_syntax0 = self.conf_namesyntax_optmenu1_SV.get()
        name_syntax1 = self.conf_namesyntax_optmenu2_SV.get()
        name_syntax2 = self.conf_namesyntax_optmenu3_SV.get()

        # Holds list of tuples of invalid elements found
        # index 0 = text explanation to user
        # index 1 = problematic user-provided element
        self.invalid_config = []

        # Checks file name for invalid characters
        self.invalid_filename_check(folder_name, "folder name")
        self.invalid_filename_check(prep_txt, "prepending text")

        # Checks for presence of selected directories
        self.invalid_dirs_check(self.new_dirs["new_out_dir"], "Output directory does not exist")
        self.invalid_dirs_check(self.new_dirs["new_inp_dir"], "Input directory does not exist")

        # Checks that the 3 syntax elements for the file name do not repeat
        if len([name_syntax0, name_syntax1, name_syntax2]) != \
           len({name_syntax0, name_syntax1, name_syntax2}):
            self.invalid_config.append(
                ("File name syntax cannot repeat elements",
                 f"{name_syntax0}, {name_syntax1}, {name_syntax2}")
            )

        # If any problematic elements have been found, notifies user, returns False
        if len(self.invalid_config) > 0:
            # Sets verbiage
            if len(self.invalid_config) == 1: element_sp = "element"
            else: element_sp = "elements"

            # User-friendly output of problem(s)
            problem_list = [f"{problem[0]}\n{problem[1]}" for problem in self.invalid_config]
            problem_list = "\n\n".join(problem_list)

            messagebox.showerror(
                title = f"Invalid {element_sp}",
                message = f"Please correct the below problematic {element_sp}:\n\n"
                          f"{problem_list}"
            )

            return False

        # Sets all elements of self.config_options
        self.config_options["exp_folder"] = folder_name.strip() # Custom folder name
        self.config_options["exp_def_dir"] = self.new_dirs["new_out_dir"].strip() # Custom output directory
        self.config_options["inp_def_dir"] = self.new_dirs["new_inp_dir"].strip() # Custom input directory
        self.config_options["prepending"]["prepend_txt"] = prep_txt.strip() # Custom prepend text
        self.config_options["prepending"]["prepend_num"] = prep_gen_num # Enable/disable prepend numbering
        self.config_options["syntax"]["0"] = name_syntax0 # File name syntax element 0
        self.config_options["syntax"]["1"] = name_syntax1 # File name syntax element 1
        self.config_options["syntax"]["2"] = name_syntax2 # File name syntax element 2

    # Checks for valid default input and output directories
    def invalid_dirs_check(self, dir: str, explanation: str):
        if dir == "": return
        if os.path.isdir(dir) == False:
            self.invalid_config.append((explanation, dir))

    # Checks given text for invalid file name characters
    def invalid_filename_check(self, text: str, field: str):
        if text == "": return
        if len(text) > 16:
            self.invalid_config.append(
                (f"Text is too long for {field} (max is 16 characters)", len(text))
            )
        for letter in text:
            if letter in self.invalid_chars:
                self.invalid_config.append(
                    ("Invalid file name character", letter)
                )

    # Exports config file
    def export_json(self):
        # First validates user inputs.
        # If anything fails, user is informed in self.check_config_inputs() and the save is canceled.
        if self.check_config_inputs() == False: return False

        # Sets newly assigned syntax options to self.config_syntax_opt so that if
        # config window is reopened, syntax options will be correct.
        self.config_syntax_opt_setup()
        self.json_handler.write_json(self.file_name, self.config_options)

    # Saves and exits config (exports config file before exit)
    def save_exit_config(self, e = None):
        # First validates user inputs.
        # If anything fails, user is informed in self.check_config_inputs() and the save and exit is canceled.
        if self.export_json() == False: return
        self.exit_config_win()

    # Simple exit from config. No save.
    def exit_config_win(self):
        self.config_win.destroy()
        self.main_win.deiconify()

    # Sets up the list of options for file name syntax
    # Default values for drop-downs are based on this order
    def config_syntax_opt_setup(self):
        syntax_opt_list = list(self.config_options["syntax"].values())
        self.config_syntax_opt = [
            syntax_opt_list[0],
            syntax_opt_list[1],
            syntax_opt_list[2]
        ]

    # Begins PDF import process.
    # Gets PDF file name, evaluates contents, divides PDF up into letters,
    # creates list of filenames to export, checks that file names don't already exist, and exports.
    def import_pdf(self, e = None):
        # Gets file name (or False if user clicked Cancel)
        import_pdf = self.pdf_handler.import_pdf(self.config_options)
        if import_pdf[1] == True: # Default input dir needs to be reset (invalid dir)
            self.config_options["inp_def_dir"] = ""
            self.json_handler.write_json(self.file_name, self.config_options)
        if import_pdf[0] == False: return # User did not choose a directory

        # Evaluates selected file
        # If validation failes, failure message to user is returned (str)
        # None returned if validation succeeds
        evaluation = self.pdf_handler.evaluate_contents(self.config_options)
        if evaluation != None: # Nothing is returns upon successful completion
            messagebox.showerror(title = "Invalid file", message = evaluation)
            return

        create_raw_list = self.pdf_handler.create_raw_filename_list()
        if create_raw_list != None: # Nothing is returns upon successful completion
            messagebox.showerror(title = "Error encountered", message = create_raw_list)
            return

        create_final_filenames = self.pdf_handler.create_filenames(self.config_options)
        if create_final_filenames != None: # Nothing is returns upon successful completion
            messagebox.showerror(title = "Error encountered", message = create_final_filenames)
            return

        # Receives three-ele tuple
        # ({bool for completed (True) or uncompleted (False) export}, {bool for resetting export dir (True) or not (False) due to invalid dir},
        # {str for exported dir if ele 0 was True OR str for message to user if ele 0 was False})
        # First ele False indicates uncompleted export
        # Second element bool indicates
        # Third ele False indicates user did not select a directory (as opposed to a failed export)
        final_export = self.pdf_handler.export_pdfs(self.config_options)
        if final_export[1] == True: # Default exp dir needs to be reset (was invalid)
            self.config_options["exp_def_dir"] = ""
            self.json_handler.write_json(self.file_name, self.config_options)
        if final_export[0] == False: # Uncompleted export
            # If ele 0 is False, there will be three elements in tuple. If error, third ele will be str
            # error message to user. Otherwise will be False (user canceled export).
            if final_export[2] == False: return # Uncompleted export due to canceled (not due to failure)
            # Uncompleted export due to failure. Ele 2 is str err msg to user
            messagebox.showerror(
                title = "Error encountered",
                message = final_export[2]
            )
            return

        # Successful export. Ele 2 is str directory where files were exported
        if messagebox.askyesno(
            title = "Successful export",
            message = "Successfully exported PDF contents.\n\nWould you like to open the export folder?"
        ): os.startfile(final_export[2])

    # This code was taken from
    # https://nitratine.net/blog/post/issues-when-using-auto-py-to-exe/#the-one-file-resource-wrapper
    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        try: base_path = sys._MEIPASS
        except Exception: base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)