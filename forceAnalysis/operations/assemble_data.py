"""
depending which 'subject' is given in the cli input ('magneto'/'lizards'), the respective data_assembly is executed.
This is magneto_data_assembly for subject "magneto" and lizard_data_assembly for subject "lizards".
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

lizard_patterns = {}


def read_in_trial_notes(date):
    """
    This function is for subject "magneto". It reads in the trial notes which were written down during the experiments.
    Each trial date should have its own dataCollectionTable with the respective date as YYYY-MM-DD attached.
    param: date: the date in the above mentioned format, passed as one of the arguments from def assemble()
    """
    print(f"In this file explorer Trial Notes please select the folder with the same trial date as {date}, which"
          f"contains the respective dataCollectionTable")
    name = "Trial Notes"
    data_folder_path = Path(auxiliaryfunctions.get_path_of_folder(name))
    file = os.path.join(data_folder_path, "dataCollectionTable_{}.xlsx".format(date))

    df_trial_notes = pd.read_excel(file)

    print(df_trial_notes.head())
    return df_trial_notes, data_folder_path


def read_in_files_magneto(date, folder_path):
    import os
    import re
    from glob import glob
    # TODO: rewrite to match sub folder structure -> go into all folders with the date in them, then into the csv folder
    # TODO: rename all folders and files in folder to include runNum in filenames, based on trial data: call func

    # OLD VERSION: all csv topics are in one folder
    #filedict = {}
    # get all csv files listed in this folder which match the stringpatterns defined in the dict
    #filelist = [f for f_ in [glob(os.path.join(folder_path, pattern[1])) for pattern in list(magneto_patterns.values())] for f in f_]
    #print('filelist: ', filelist, '\nvalues: ', list(magneto_patterns.values()))

    # NEW VERSION: all csv topics are in a folder "csv" within another folder for each trial, each of which is in the selected folder path
    # go through all trial folders (YYYY-MM-DD-hh-mm-ss) in selected folder which contain the selected date YYYY-MM-DD,
    # then got to the csv folder in that folder. Rename all csv files to contain the time/second half of the trial folder:
    # hh-mm-ss within the filename.
    # add all csv files which match the magneto_file_patterns as a list to a list.
    # after going through all trial foulders the filelist will be a list with many filedicts, hence this needs to be flattened and combined to one big filedict

    # find all trial folders in the selected folder which contain the passed date string
    trial_folder_list = []
    reg_compile = re.compile("\d{4}-\d{2}-\d{2}")
    for dirpath, dirnames, _ in os.walk(folder_path):
        trial_folder_list = trial_folder_list + [dirname for dirname in dirnames if reg_compile.match(dirname)]
    print("trial folder list: ", trial_folder_list)

    # create an overall list to collect all filedicts for every folder:
    filedicts_for_trialdate = []
    # one dict for all filedicts (keep same keys but merge values)
    merged_filedict = dict(zip(magneto_patterns.keys(), [None]*len(magneto_patterns.keys())))
    print("merged filedict: ", merged_filedict)


    no_files_list = []
    # go through each trial folder, go to the csv folder within it and create a filedict for that trial folder
    print("adding trial date to filenames...")
    for trial_folder in trial_folder_list:
        filedict = {}
        path = os.path.join(folder_path, trial_folder)
        csv_folder_path = os.path.join(path, "csv")

        # rename all .csv files in the csv folder to include the date and time in the filename
        # only if date and time not already in filename
        csv_file_list = glob(os.path.join(csv_folder_path, "*.csv"))
        for csv_file in csv_file_list:
            # use this section if data accidentally contained twice in filename now:
            # works if original files start with "magneto"
            keep_from = "magneto"
            pure_file_name = csv_file.rsplit(os.path.sep, 1)[1]
            orig_file_name = pure_file_name.partition(keep_from)[1] + "_" + pure_file_name.partition(keep_from)[2]
            #print("filename reset: ", orig_file_name)

            new_csv_name = trial_folder + "_" + orig_file_name
            #print("new csv name: ", new_csv_name)

            os.rename(csv_file, os.path.join(csv_folder_path, new_csv_name))

        # create a file dict for each trial folder
        # get all the csv files which match any of the pre-defined name patterns to include only files of sensors of interest
        filelist = [f for f_ in [glob(os.path.join(csv_folder_path, pattern[1])) for pattern in list(magneto_patterns.values())] for f in f_]
        print("filelist: ", filelist)


        if len(filelist) > 0:
            pass
        else:
            print("WARNING: no files found")
            no_files_list.append(trial_folder)
            #exit()

        # creates individual lists for each element in magneto_patterns.keys()
        for element in magneto_patterns.keys():
            filedict[element] = [file for file in filelist if file.find(magneto_patterns[element][0]) > 0]
        #print("filedict:\n", "{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in filedict.items()) + "}")

        filedicts_for_trialdate.append(filedict)

    print("filedicts_for_trialdate: ", filedicts_for_trialdate)

    #print("filedict merged empty: ", merged_filedict)

    # now we have a list of filedicts, each of those filedicts has the same keys but different values.
    # make one big dict, with the same keys but combining all values of all filedicts for that key
    for filedict in filedicts_for_trialdate:
        # merged filedict empty:  {'force': None, 'imu': None, 'FR_pos': None, 'FL_pos': None, 'HR_pos': None, 'HL_pos': None, 'power': None}
        for k,v in filedict.items():
            if merged_filedict[k] is None:
                #print("value for key is None")
                # append the list to the key to overwrite initial None value
                merged_filedict[k] = v
            else:
                #print("value is not None and file will be added to list")
                # append filename v[0] which is in list (v)
                merged_filedict[k] = merged_filedict[k] + v


    print("merged filedict flattened: \n", merged_filedict)

    print("missing files for: ", no_files_list)

    return merged_filedict


def read_in_files_lizards():
    return


def add_runNum_to_filenames():
    """goes through all files in all data folders and adds runNum to filename, based on the trial data notes."""
    return


### MAIN FUNTION called by cli.py argument
def assemble(subject, date, overwrite_csv_files):
    """
    this function is called by the click argument assemble_force_data(**args) and takes the following arguments:
    subject: String "magneto" or "lizards"
    date: String format as YYYY-MM-DD
    """
    print(subject)
    if subject == "magneto":
        # read in all files that match defined string patterns to not import all bag topics
        # creates a dict with several files (csv topics) for each element in magneto_patterns.keys()

        # read in the trial data (notes on velocity, fails etc.)
        df_trial_notes, data_folder_path = read_in_trial_notes(date)

        merged_filedict = read_in_files_magneto(date, data_folder_path)

        # EXECUTES THIS FUNCTION OF THE RESPECTIVE MODULE
        magneto_data_assembly(merged_filedict, overwrite_csv_files, df_trial_notes, date)

    elif subject == "lizards":
        filedict = read_in_files_lizards()
    else:
        print("no such subject defined")
    return


