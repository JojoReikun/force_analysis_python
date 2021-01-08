"""
this script creates an excel sheet for every run and fills in relevant information, which are partly pre-assembled
in the dict.
"""

### IMPORTS
import numpy as np
import pandas as pd
import os

# contains all "static" data for all runs
# startposition: 0 = straight up, -10 rotated 10 deg to left, 10 rotated 10 deg to the right, NAN if run on ground or in air
# failreason describes if the failedfoot did not attach when it was its turn or another failedfoot detached while the other moved
# if failed variables are all NAN, the trial was complete (3 complete cycles)
run_info = {'run2': {'velocity': 0.5,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 4,
                     'failedfoot': 'HR',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run3': {'velocity': 0.5,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True},
            'run4': {'velocity': 0.5,
                     'footfallpattern': ['HL', 'FR', 'FL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 2,
                     'failedfoot': 'FR',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run5': {'velocity': 0.5,
                     'footfallpattern': ['FR', 'HR', 'FL', 'HL'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 3,
                     'failedfoot': 'FL',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run6': {'velocity': 0.5,
                     'footfallpattern': ['FR', 'HL', 'FL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 1,
                     'failedfoot': 'FR',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run7': {'velocity': 0.5,
                     'footfallpattern': ['FR', 'HL', 'HR', 'FL'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 4,
                     'failedfoot': 'FL',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run8': {'velocity': 0.5,
                     'footfallpattern': ['FR', 'HL', 'HR', 'FL'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 7,
                     'failedfoot': 'FR',
                     'failreason': 'detached',
                     'forcesbiased': True},
            'run9': {'velocity': 0.25,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 2,
                     'failedfoot': 'FR',
                     'failreason': 'detached, FR coxa failed',
                     'forcesbiased': True},
            'run10': {'velocity': 0.25,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True},
            'run11': {'velocity': 0.25,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True},
            'run12': {'velocity': 0.25,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': -10,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True},
            'run13': {'velocity': 0.25,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 10,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True},
            'run14': {'velocity': 0.25,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': np.nan,
                     'surface': 'air',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True},
            'run15': {'velocity': 0.25,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': np.nan,
                     'surface': 'ground',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True}
            }

# defines the numbers of the relevant columns for each topic
# position and orientation for each foot are in m relative to the center of the body - coord sys:
# AL/FL: +x|+y|-z, AR/FR: +x|-y|-z, BL/HL: -x|+y|-z, BR/HR: -x|-y|-z
magneto_columnnames_dict = {"force": {"force_x": 9,
                                      "force_y": 10,
                                      "force_z": 11},
                            "imu": {"imu_linacc_x": 19,
                                    "imu_linacc_y": 20,
                                    "imu_linacc_z": 21},
                            "FR_pos": {"FR_pos_x": 85,
                                         "FR_pos_y": 86,
                                         "FR_pos_z": 87,
                                         "FR_orient_x": 89,
                                         "FR_orient_y": 90,
                                         "FR_orient_z": 91},
                            "FL_pos": {"FL_pos_x": 85,
                                         "FL_pos_y": 86,
                                         "FL_pos_z": 87,
                                         "FL_orient_x": 89,
                                         "FL_orient_y": 90,
                                         "FL_orient_z": 91},
                            "HL_pos": {"HL_pos_x": 85,
                                         "HL_pos_y": 86,
                                         "HL_pos_z": 87,
                                         "HL_orient_x": 89,
                                         "HL_orient_y": 90,
                                         "HL_orient_z": 91},
                            "HR_pos": {"HR_pos_x": 85,
                                         "HR_pos_y": 86,
                                         "HR_pos_z": 87,
                                         "HR_orient_x": 89,
                                         "HR_orient_y": 90,
                                         "HR_orient_z": 91}
                            }     # force_x, force_y, force_z named "x", "y", "z" in csv file

magneto_raw_dict = {}



def fill_trial_note_data():
    """
    this function fills in the run specific data from the notes, e.g. velocity, sensorfoot etc.
    and adds to run_data_dict
    :return:
    """
    return


def fill_file_data(filedict):
    """
    reads in file by file (run) and adds data to run_data_dict
    """
    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions

    for n in range(len(list(filedict.values())[0])):  # loops through number of files
        # contains all data for one run
        run_data_dict = {}

        run = list(filedict.values())[0][n]    # takes the n file of the first topic to get the run number
        print("\n ---- run: ", run)
        run_number = run.rsplit(os.sep, 1)[1]
        run_number = run_number.split("_", 1)[0]
        print("run number: {}".format(run_number))

        columnnames = []
        for topic in list(filedict.keys()):
            # TODO: check order of loops and that run_data_dict actually contains all topics from 1 run
            print("TOPIC: {} ".format(topic))

            # read the file of the current run, which belongs to topic
            # instead of using n make sure the file fits the run number
            file = [f for f in filedict[topic] if run_number in f][0]
            print("file: ", file)

            data = pd.read_csv(file)

            # drop empty rows in df:
            data.dropna(axis=0)

            # creates a new empty dict which is filled with the subtopics, e.g. force_x, force_y, force_z for topic force
            sub_topic_dict = {}
            for item in range(len(magneto_columnnames_dict[topic])):
                #print("item: ", item)
                columnname = list(magneto_columnnames_dict[topic].keys())[item]
                #print("columnname: ", columnname)
                sub_topic_dict[columnname] = data.iloc[:, list(magneto_columnnames_dict[topic].values())[item]].values
            #print("subtopic dict: ", sub_topic_dict)

            run_data_dict[topic] = sub_topic_dict

            #print("run_data_dict: \n", "{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in run_data_dict.items()) + "}")

            # save run_data_dict:
            filename = run_number + "_assembled"
            # convert dict to data frame:
            # determine the longest column in run_data_dict.values() use that for df
            for topic in list(run_data_dict.values()):  # list of dicts with the subtopics
                old_max_length = 0
                for subname, subtopic in topic.items():   # list with data for every subtopic

                    print("subname: ", subname, "\nsubtopic: ", subtopic)
                    columnnames.append(subname)

                    #print("old_max_length: ", old_max_length)
                    max_length = len(subtopic)
                    if old_max_length > max_length:
                        max_length = old_max_length
                    old_max_length = max_length

            print("columnnames: ", columnnames)
            run_data_df = pd.DataFrame(columns=columnnames, index=range(max_length))
            print("run_data_df: \n", run_data_df)
            # TODO: fill up dataframe:


            path = os.path.join(os.getcwd(), "assembled_csv")
            auxiliaryfunctions.attempttomakefolder(path)
            run_data_df.to_csv(os.path.join(path, "{}.csv".format(filename)), index=True, header=True)

            magneto_raw_dict[run_number] = run_data_dict
    # print("\n\n------------------------------\n\n",
    #       "magneto_raw_dict: \n", "{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in magneto_raw_dict.items()) + "}")
    return


def magneto_data_assembly(filedict):
    print("\nmagneto data assembly")
    fill_file_data(filedict)
    return
