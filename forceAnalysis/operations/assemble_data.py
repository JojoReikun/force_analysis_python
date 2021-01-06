"""
depending which 'subject' is given in the cli input ('magneto'/'lizards'), the respective data_assembly is executed.
assembled data frame will be saved to csv file for every file
"""

### IMPORTS
from forceAnalysis.utils import auxiliaryfunctions
from glob import glob
import os
from pathlib import Path

# define stringpatterns = patterns in the csv filenames which belong to the respective relevant bag file topics
magneto_patterns = {"force": ("contact_force", "*contact_force*.csv"),
                    "imu": ("imu_raw_slash_data", "*imu_raw_slash_data*.csv")}
# defines the numbers of the relevant columns for each topic
magneto_columnnames_dict = {"force": [9, 10, 11]}     # force_x, force_y, force_z named "x", "y", "z" in csv file


def read_in_files_magneto():
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
    print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in filedict.items()) + "}")
    return filedict


def read_in_files_lizards():
    return


def assemble(subject):
    print(subject)
    if subject == "magneto":
        # read in all files that match defined string patterns to not import all bag topics
        # creates a dict with several files (csv topics) for each element in magneto_patterns.keys()
        filedict = read_in_files_magneto()
    elif subject == "lizards":
        filedict = read_in_files_lizards()
    else:
        print("no such subject defined")
    return


