"""
depending which 'subject' is given in the cli input ('magneto'/'lizards'), the respective data_assembly is executed.
assembled data frame will be saved to csv file for every file
"""

### IMPORTS
from forceAnalysis.utils import auxiliaryfunctions
from forceAnalysis.operations.magneto_data_assembly import magneto_data_assembly
from glob import glob
import os
import pandas as pd
from pathlib import Path

# define stringpatterns = patterns in the csv filenames which belong to the respective relevant bag file topics
magneto_patterns = {"force": ("contact_force", "*contact_force*.csv"),
                    "imu": ("imu_raw_slash_data", "*imu_raw_slash_data*.csv"),
                    'FR_pos': ("AR_slash_state", "*AR_slash_state.csv"),
                    'FL_pos': ("AL_slash_state", "*AL_slash_state.csv"),
                    'HR_pos': ("BR_slash_state", "*BR_slash_state.csv"),
                    'HL_pos': ("BL_slash_state", "*BL_slash_state.csv"),
                    'power': ("polaris_jr_pwr_status", "*polaris_jr_pwr_status*.csv")
                    }


def read_in_trial_notes():
    data_folder_path = Path(auxiliaryfunctions.get_path_of_folder())
    file = os.path.join(data_folder_path, "dataCollectionTable.xlsx")
    df_trial_notes = pd.read_excel(file)
    print(df_trial_notes.head())
    return df_trial_notes


def read_in_files_magneto():
    # TODO: rewrite to match subfolder structure
    # TODO: rename all folders and files in folder to include runNum in filenames, based on trial data: call func
    folder_path = Path(auxiliaryfunctions.get_path_of_folder())
    print("selected folder path: ", folder_path)

    filedict = {}
    # get all csv files listed in this folder which match the stringpatterns defined in the dict
    filelist = [f for f_ in [glob(os.path.join(folder_path, pattern[1])) for pattern in list(magneto_patterns.values())] for f in f_]
    print('filelist: ', filelist, 'values: ', list(magneto_patterns.values()))

    if len(filelist) > 0:
        pass
    else:
        print("WARNING: no files found")
        exit()

    # creates individual lists for each element in magneto_patterns.keys()
    for element in magneto_patterns.keys():
        filedict[element] = [file for file in filelist if file.find(magneto_patterns[element][0]) > 0]
    print("filedict:\n", "{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in filedict.items()) + "}")
    return filedict


def read_in_files_lizards():
    return


def add_runNum_to_filenames():
    """goes through all files in all data folders and adds runNum to filename, based on the trial data notes."""
    return


### MAIN FUNTION called by cli.py argument
def assemble(subject, overwrite_csv_files):
    print(subject)
    if subject == "magneto":
        # read in all files that match defined string patterns to not import all bag topics
        # creates a dict with several files (csv topics) for each element in magneto_patterns.keys()

        # read in the trial data (notes on velocity, fails etc.)
        df_trial_notes = read_in_trial_notes()

        filedict = read_in_files_magneto()

        magneto_data_assembly(filedict, overwrite_csv_files, df_trial_notes)

    elif subject == "lizards":
        filedict = read_in_files_lizards()
    else:
        print("no such subject defined")
    return


