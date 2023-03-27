"""
depending on which 'subject' is given in the cli input ('magneto'/'lizards'), the respective data_assembly is executed.
This is magneto_data_assembly for subject "magneto" and lizard_data_assembly for subject "lizards".
assembled data frame will be saved to csv file for every file
"""

### IMPORTS
from forceAnalysis.utils import auxiliaryfunctions
from forceAnalysis.operations import magneto_data_assembly
from glob import glob
import os
import pandas as pd
from pathlib import Path
import pprint
import errno

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
    This function is for subject "magneto". It reads in the trial notes which were written down during the experiments,
    a dataCollectionTable_all or dataCollectionTable_YYYY-MM-DD xlsx file.
    Each trial date should have its own dataCollectionTable with the respective date as YYYY-MM-DD attached, plus there
    is a table for all files combines too.
    param: date: if no date is passed "all" will be used. Otherwise, this is a string of the date in the
    above-mentioned format, passed as one of the arguments from def assemble() in the console.
    """

    if date == "all":
        """loop to handle reading in all data trials rather than just one specific date. 
        User will be asked to select the "experiments" folder which contains all trial folders"""

    else:
        """one specific date is given to only look at that trial set.
        User will be asked to select folder to that date specifically."""

        print(f"In this file explorer Trial Notes please select the folder with the same trial date as {date}, which"
              f" contains the respective dataCollectionTable_{date} xlsx file also.")
        name = f"Trial Notes for {date}"
        data_folder_path = Path(auxiliaryfunctions.get_path_of_folder(name))
        trial_folder_name = str(data_folder_path).rsplit(os.sep)[-1]
        print(f"trial_folder_name: {trial_folder_name}")

        if any(char.isdigit() for char in trial_folder_name) and trial_folder_name == date:
            print(f"opening excel file: dataCollectionTable_{date}.xlsx")
            file = os.path.join(data_folder_path, "dataCollectionTable_{}.xlsx".format(date))
            df_trial_notes = pd.read_excel(file)
            print(df_trial_notes.head())

            if df_trial_notes.empty:
                print(f"couldn't open: dataCollectionTable_{date}.xlsx")
                exit()
        else:
            print(f"selected folder does not follow date format of YYYY-MM-DD or folder date does not match entered date from console!")
            exit()

        # If folder follows date format and dataCollectionTable is in folder, then continue to read files.

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
    # then go to the csv folder in that folder.
    # Rename all csv files to contain the time/second half of the trial folder: hh-mm-ss within the filename.
    # add all csv files which match the magneto_file_patterns as a list to a list.
    # after going through all trial folders the filelist will be a list with many filedicts, hence this needs to be flattened and combined to one big filedict


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
    no_csv_list = []
    # go through each trial folder, go to the csv folder within it and create a filedict for that trial folder

    for trial_folder in trial_folder_list:
        filedict = {}
        path = os.path.join(folder_path, trial_folder)
        csv_folder_path = os.path.join(path, "csv")

        # TODO: check if folder "csv" exists, else add this trial folder to list for need_of_bag_conversion,
        # Todo: use no_csv_list to skip these trial folders for now so later there is no issues in merging trial notes and magneto data
        if not os.path.isdir(csv_folder_path):
            no_csv_list.append(path)

        else:
            # rename all .csv files in the csv folder to include the date and time in the filename
            # only if date and time not already in filename
            csv_file_list = glob(os.path.join(csv_folder_path, "*.csv"))

            # create a string pattern to match. If csv contains date already it will match! No renaming then.
            reg_compile = re.compile("\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}.*")\
            # TODO: if there are more runs than desired dataset in trial folder: add option to enter selected trial
            #  interval or instead of trial folder have user select the relevant folders! (currently moved trial folders with other foot ratios in new folder for 2021-03-31)
            for csv_file in csv_file_list:
                #print(f"csv_file: {csv_file}")
                csv_file_filename = csv_file.rsplit(os.path.sep)[-1]
                #print(f"csv_file_filename: {csv_file_filename}")
                if reg_compile.match(csv_file_filename):
                    #print("filename already contains date")
                    continue
                else:
                    # use this section if data accidentally contained twice in filename now:
                    # works if original files start with "magneto"
                    print("adding trial date to filenames...")
                    keep_from = "magneto"
                    pure_file_name = csv_file.rsplit(os.path.sep, 1)[1]
                    print("pure filename: ", pure_file_name)
                    orig_file_name = pure_file_name.partition(keep_from)[1] + "_" + pure_file_name.partition(keep_from)[2].lstrip("_")
                    print("filename reset: ", orig_file_name)

                    new_csv_name = trial_folder + "_" + orig_file_name
                    print("new csv name: ", new_csv_name)

                    os.rename(csv_file, os.path.join(csv_folder_path, new_csv_name))

            # create a file dict for each trial folder
            # get all the csv files which match any of the pre-defined name patterns to include only files of sensors of interest
            filelist = [f for f_ in [glob(os.path.join(csv_folder_path, pattern[1])) for pattern in list(magneto_patterns.values())] for f in f_]
            print("filelist: ", filelist)

            if len(filelist) > 0:
                pass

            else:
                print("WARNING: no files for Magneto sensor data found")
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

    # print("merged filedict flattened: \n")
    # pprint.pprint(merged_filedict)

    print("--- missing Magneto data files for: ", no_files_list)

    print(f"--- no csv folders in: ")
    for item in no_csv_list:
        print(f"{item})")
    if len(no_csv_list) > 0:
        print(f"for these files you need to convert bag files or check for missing bag files first.")
    else:
        print("All csv files complete.")

    return merged_filedict, no_csv_list


def read_in_files_lizards():
    return


def add_runNum_to_filenames():
    """goes through all files in all data folders and adds runNum to filename, based on the trial data notes."""
    return


### MAIN FUNTION called by cli.py argument
def assemble(subject, date):
    """
    this function is called by the click argument assemble_force_data(**args) and takes the following arguments:
    subject (optional): String "magneto" or (to come in future) "lizards"
    date (optional): String format as YYYY-MM-DD
    This is now modified to: If date is given, only data for this date will be assembled, otherwise all trials will be
    read and assembled in one big data frame.
    """
    print(f"Subject: {subject}, Date: {date}")

    if subject == "magneto":
        # read in all files that match defined string patterns to not import all bag topics
        # creates a dict with several files (csv topics) for each element in magneto_patterns.keys()

        # read in the trial data (notes on velocity, fails etc.)
        df_trial_notes, data_folder_path = read_in_trial_notes(date)

        # read in sensor data from magneto, trials with no csv files will be ignored in further process
        # --> check for missing or not converted bag files in respective trial folder
        merged_filedict, no_csv_list = read_in_files_magneto(date, data_folder_path)

        # EXECUTES THIS FUNCTION OF THE RESPECTIVE MODULE magneto_data_assembly.py
        magneto_data_assembly.magneto_data_assembly(merged_filedict, df_trial_notes, date, no_csv_list, data_folder_path)

        print("DONE! Data assembly complete!")

    elif subject == "lizards":
        filedict = read_in_files_lizards()
    else:
        print("Default subject magneto will be used.")
        subject = "magneto"
    return


