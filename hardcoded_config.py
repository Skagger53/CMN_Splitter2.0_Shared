# These are the default configuration values.
# These are used if the configuration file is corrupt/removed and the user opts to reset to defaults, or
# if the user chooses the reset to defaults option.
default_cfg = {
  "config_len": 14, # Length of JSON file

  "center_window": 1, # 0 = False (main window not centered), 1 = True (centered)

  "window_size": # Main window only
    {
      "window_x": 248,
      "window_y": 280
    },

  "window_title": "CMN Splitter", # Main window only

  "exp_folder": "", # "" = auto-generated folder output name

  "prepending": # Items to prepend every created PDF
    {
      "prepend_txt": "Case mix", # Optional prepended text. Always precedes num if both enabled.
      "prepend_num": 0 # 0 = No prepended num; 1 = use prepended num (e.g., "CM001")1
    },

  "syntax": # Syntax for exported PDFs' names (e.g., "DoeJohn_RAD_2022.09.01.pdf")
    {
      "0": "Patient name", # Patient name -- HARD CODED (not case-sensitive)
      "1": "Case Mix", # Case mix code -- HARD CODED (not case-sensitive)
      "2": "Effective date" # Effective date -- HARD CODED (not case-sensitive)
    },


  "exp_def_dir": "", # Default export directory

  "inp_def_dir": "", # Default input directory

  "invalid_chars": # Disallowed characters for custom file and folder names
    [
      "#", "%", "&", "{", "}", "\\", "<", ">", "*", "?", "/", "$", "!", "\"", "'", ":", "@", "+"
    ],

  # Validation checks
  # first list element = index of imported page 0 text broken up by new line (meaning page 0, line X)
  # second list element = text that first element should contain
  "file_valid1": [0, "MINNESOTA DEPARTMENT OF HEALTH"],
  "file_valid2": [1, "Case Mix Review Program, Health Regulation Division"],

  "extraction_settings": {
    "date_format": "%m/%d/%Y", # datetime.datetime format used in notice
  # [{text in ele before name}, {text imm preceding date}, {char offset for name}, {date str length}, {text in ele after code}]
    "name_date_extract": ["THIS IS NOT A BILL", "EFFECTIVE ON: ", -11, -10, "EFFECTIVE ON: "],
    "code_list": ["ES3", "ES2", "ES1", "RAE", "RAD", "RAC", "RAB", "RAA", "HE2", "HE1", "HD2", "HD1", "HC2", "HC1",
                  "HB2", "HB1", "LE2", "LE1", "LD2", "LD1", "LC2", "LC1", "LB2", "LB1", "CE2", "CE1", "CD2", "CD1",
                  "CC2", "CC1", "CB2", "CB1", "CA2", "CA1", "BB2", "BB1", "BA2", "BA1", "PE2", "PE1", "PD2", "PD1",
                  "PC2", "PC1", "PB2", "PB1", "PA2", "PA1", "AAA", "DDF"] # All Case Mix codes
  },

  # Configuration for error log
  "err_log": {
    "file_name": "error_log.txt", # Name of error log file
    "err_log_len": 20 # Max number of error logs to keep (oldest will drop off when more are added)
  }
}