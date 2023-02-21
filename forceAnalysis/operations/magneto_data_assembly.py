"""
this script creates an excel sheet for every run and fills in relevant information, which are partly pre-assembled
in the dict.
"""

### IMPORTS
import numpy as np
import pandas as pd
import os
from glob import glob

# contains all "static" data for all runs for 28-10-2020 data collection
# startposition: 0 = straight up, -10 rotated 10 deg to left, 10 rotated 10 deg to the right, NAN if run on ground or in air
# failreason describes if the failedfoot did not attach when it was its turn or another failedfoot detached while the other moved
# if failed variables are all NAN, the trial was complete (3 complete cycles)
run_info = {'run2': {'velocity': 0.5,
                     'step_frequency': 0.5,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 4,
                     'failedfoot': 'HR',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            # run 2: CHANGE: moved target tip position of all feet from 20 to 25 (cm) -->
            # y distance from centre to foot tip -->
            # feet parallel aligned to the wall from the beginning
            'run3': {'velocity': 0.5,
                     'step_frequency': 0.5,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': np.nan,
                     'failedfoot': np.nan,
                     'failreason': np.nan,
                     'forcesbiased': True},
            'run4': {'velocity': 0.5,
                     'step_frequency': 0.5,
                     'footfallpattern': ['HL', 'FR', 'FL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 2,
                     'failedfoot': 'FR',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run5': {'velocity': 0.5,
                     'step_frequency': 0.5,
                     'footfallpattern': ['FR', 'HR', 'FL', 'HL'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 3,
                     'failedfoot': 'FL',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run6': {'velocity': 0.5,
                     'step_frequency': 0.5,
                     'footfallpattern': ['FR', 'HL', 'FL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 1,
                     'failedfoot': 'FR',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run7': {'velocity': 0.5,
                     'step_frequency': 0.5,
                     'footfallpattern': ['FR', 'HL', 'HR', 'FL'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 4,
                     'failedfoot': 'FL',
                     'failreason': 'did not attach',
                     'forcesbiased': True},
            'run8': {'velocity': 0.5,
                     'step_frequency': 0.5,
                     'footfallpattern': ['FR', 'HL', 'HR', 'FL'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 7,
                     'failedfoot': 'FR',
                     'failreason': 'detached',
                     'forcesbiased': True},
            # run 8: failed after 1 complete cycle and 3 steps: FR detached when FL was about to move
            # recorded testing after running (in air and on ground),
            # therefore only start of file interesting (big file)
            'run9': {'velocity': 0.25,
                     'step_frequency': 0.5,
                     'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                     'direction': 0,
                     'surface': 'wall',
                     'sensorfoot': 'FR',
                     'failedstep': 2,
                     'failedfoot': 'FR',
                     'failreason': 'detached, FR coxa failed',
                     'forcesbiased': True},
            'run10': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'FR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': True},
            'run11': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'FR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': True},
            'run12': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': -10,
                      'surface': 'wall',
                      'sensorfoot': 'FR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': True},
            'run13': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 10,
                      'surface': 'wall',
                      'sensorfoot': 'FR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': True},
            'run14': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': np.nan,
                      'surface': 'air',
                      'sensorfoot': 'FR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': True},
            'run15': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': np.nan,
                      'surface': 'ground',
                      'sensorfoot': 'FR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': True},
            'run16': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': np.nan,
                      'surface': 'air',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run17': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': np.nan,
                      'surface': 'ground',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run18': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run19': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run20': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run21': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': -10,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run22': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 10,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run23': {'velocity': 0.25,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run24': {'velocity': 0.5,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': 4,
                      'failedfoot': 'FL',
                      'failreason': 'detached',
                      'forcesbiased': False},
            'run25': {'velocity': 0.5,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run26': {'velocity': 0.5,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run27': {'velocity': 0.75,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': 1,
                      'failedfoot': "FR",
                      'failreason': "did not attach",
                      'forcesbiased': False},
            'run28': {'velocity': 0.75,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': 5,
                      'failedfoot': "FR",
                      'failreason': "did not attach",
                      'forcesbiased': False},
            # CHANGE: step_frequency reconfigured from 0.5 to 0.75, because the points were moving away too fast,
            # therefore only swing phase time changed before because motors have to cover more distance in less time
            # not so stance phase time.
            'run29': {'velocity': 0.75,
                      'step_frequency': 0.75,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': 6,
                      'failedfoot': "FL",
                      'failreason': "did not attach",
                      'forcesbiased': False},
            'run30': {'velocity': 0.75,
                      'step_frequency': 1.0,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': 6,
                      'failedfoot': "FL",
                      'failreason': "did not attach",
                      'forcesbiased': False},
            # run 30: Still reaching, it seems to move target points even faster when increasing step_frequency?
            'run31': {'velocity': 0.5,
                      'step_frequency': 1.0,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            'run32': {'velocity': 0.25,
                      'step_frequency': 1.0,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 0,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            # backward walking:
            'run33': {'velocity': 0.5,
                      'step_frequency': 0.5,
                      'footfallpattern': ['FR', 'FL', 'HL', 'HR'],
                      'direction': 180,
                      'surface': 'wall',
                      'sensorfoot': 'HR',
                      'failedstep': np.nan,
                      'failedfoot': np.nan,
                      'failreason': np.nan,
                      'forcesbiased': False},
            }

# defines the numbers of the relevant columns for each topic
# position and orientation for each foot are in m relative to the center of the body - coord sys:
# AL/FL: +x|+y|-z, AR/FR: +x|-y|-z, BL/HL: -x|+y|-z, BR/HR: -x|-y|-z
magneto_columnnames_dict = {"force": {"force_x": 9,
                                      "force_y": 10,
                                      "force_z": 11,
                                      "force_timestamp": 0},
                            "imu": {"imu_linacc_x": 19,
                                    "imu_linacc_y": 20,
                                    "imu_linacc_z": 21,
                                    "imu_timestamp": 0},
                            "FR_pos": {"FR_pos_x": 85,
                                       "FR_pos_y": 86,
                                       "FR_pos_z": 87,
                                       "FR_orient_x": 89,
                                       "FR_orient_y": 90,
                                       "FR_orient_z": 91,
                                       "FR_timestamp": 0},
                            "FL_pos": {"FL_pos_x": 85,
                                       "FL_pos_y": 86,
                                       "FL_pos_z": 87,
                                       "FL_orient_x": 89,
                                       "FL_orient_y": 90,
                                       "FL_orient_z": 91,
                                       "FL_timestamp": 0},
                            "HL_pos": {"HL_pos_x": 85,
                                       "HL_pos_y": 86,
                                       "HL_pos_z": 87,
                                       "HL_orient_x": 89,
                                       "HL_orient_y": 90,
                                       "HL_orient_z": 91,
                                       "HL_timestamp": 0},
                            "HR_pos": {"HR_pos_x": 85,
                                       "HR_pos_y": 86,
                                       "HR_pos_z": 87,
                                       "HR_orient_x": 89,
                                       "HR_orient_y": 90,
                                       "HR_orient_z": 91,
                                       "HR_timestamp": 0},
                            'power': {"voltage_15v": 8,
                                      "current_15v": 11,
                                      "power_timestamp":0}
                            }  # force_x, force_y, force_z named "x", "y", "z" in csv file

magneto_raw_dict = {}


def fill_trial_note_data_from_dict(path, run_number_runs):
    """
    this function fills in the run specific data from the notes, e.g. velocity, sensorfoot etc.
    and adds these information to the run file.
    This function uses the above defined run_info dict to add the respective info to the respective run.
    Data collection 28-10-2020
    :return:
    """

    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions
    from glob import glob

    print("\nfilling in >static< trial data from run_info dict...")

    pd.set_option('max_columns', None)

    filelist = []
    for file in glob(os.path.join(path, "*.csv")):
        filelist.append(file)

    # filter for "_assembled" in filename:
    filelist = [file for file in filelist if "_assembled" in file]

    #print("filelist: ", filelist)

    # read in files one by one and add trial notes to dataframe:
    # TODO: check here if file is in no_csv_folder and if so skip this file!
    for i, file in enumerate(filelist):
        print("Progress: ", i, "/", len(filelist), f" - File: {file}")
        run_number = file.rsplit(os.sep, 1)[1]
        run_number = run_number.split("_", 1)[0]
        #print("\n--- run: ", run_number)
        data = pd.read_csv(file)

        rows_count = data.shape[0]
        #print("rows_count: ", rows_count)
        # TODO: add column to dataframe with trial info belonging to run_number
        # check if run has entry in run_info dict
        if run_number in run_number_runs:
            for k, v in run_info[run_number].items():
                #print(k, v)
                appendlist = [v] * rows_count
                data[k] = appendlist

        #print("\n", data.head(), "\n")
        #overwrite previous assembled csv with trial notes filled in
        filename = run_number + "_assembled"
        data.to_csv(os.path.join(path, "{}.csv".format(filename)), index=False, header=True)

    return


def fill_trial_note_data_from_file(path, df_trial_notes):
    """
        this function fills in the run specific data from the trial notes (dataCollectionTable_*), e.g. velocity, sensor foot etc.
        and adds these information to the run file, which contains the previously assembled Magneto sensor data (*_assembled.csv).
        This function uses the dataCollectionTable which contains this information for all runs for that trial.
        Data collection Mar/Apr 2021 (Magneto@USC)
        :return: saves the combined assembled file as "*assembled_meta.csv"
        """

    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions
    from glob import glob

    print("\n -- filling in >static< trial data from dataCollectionTable...\n")

    pd.set_option('max_columns', None)

    #print(f"df_trial_notes: {df_trial_notes.head()}")

    # clear all unfinished columns where time is NA:
    df_trial_notes = df_trial_notes[df_trial_notes["time"].notna()]

    # add a column to df_trial_notes which combined date and time in the same format (except missing ss) as filenames
    df_trial_notes["date"] = df_trial_notes["date"].astype(str)
    # convert time first to integer to get rid of the ".0", then to string
    df_trial_notes["time"] = df_trial_notes["time"].astype(int)
    df_trial_notes["time"] = df_trial_notes["time"].astype(str)
    f_add_dash = lambda x: (x[:2] + "-" + x[2:])    # add dash to middle of each time entry to split hh and mm
    df_trial_notes["time2"] = df_trial_notes["time"].apply(f_add_dash)
    df_trial_notes["date_time"] = df_trial_notes['date'] + "-" + df_trial_notes['time2']

    # print(df_trial_notes["date_time"])

    filelist = []
    for file in glob(os.path.join(path, "*.csv")):
        filelist.append(file)

    # filter for "_assembled" in filename:
    filelist = [file for file in filelist if "_assembled" in file]

    # prints the list of all the previously _assembled.csv files
    print("filelist: ", filelist)

    # read in files one by one and add trial notes to _assembled dataframe:
    for i, file in enumerate(filelist):
        print("\nProgress: ", i, "/", len(filelist))
        filename = file.rsplit(os.sep, 1)[1]
        date_time_stamp = filename.split("_", 1)[0]    # should be date and time
        print("---> run: ", date_time_stamp)
        # this gets rid of the seconds in the stamp, so it's comparable to the date_time column
        date_time_stamp_no_ss = date_time_stamp.rsplit("-", 1)[0]
        print("df_trial_notes preview: \n", df_trial_notes.head())

        # find the matching row in the df_trial_note dataframe which matches the date_time_stamp_no_ss of _assembled file:
        correct_row = df_trial_notes[df_trial_notes["date_time"] == date_time_stamp_no_ss]
        print("correct row: ", correct_row)
        columns_to_attach = df_trial_notes.columns
        print("columns to attach: ", columns_to_attach)
        data = pd.read_csv(file)

        rows_count = data.shape[0]

        for col in columns_to_attach:
            #print("correct_row_data & length: ", correct_row[col].values, len(correct_row[col].values))
            attach_data = [correct_row[col].values[0]] * rows_count
            #print("attach data: ", attach_data[1])

            data[col] = attach_data


        #print(data.head())
        save_filename = date_time_stamp + "_assembled_meta"
        data.to_csv(os.path.join(path, "{}.csv".format(save_filename)), index=False, header=True)

        print(f"saved file: {save_filename}.csv to: {path}")

    print("Done adding trial notes to sensor data, now you can proceed to create a summary file to combine all runs.\n"
          "use forceAnalysis.create_summary(date) [date format: >>YYYY-MM-DD<<] for this")

    return


def fill_file_data(filedict, path):
    """
    reads in file by file (run) and adds data to run_data_dict. This combines all data from the different sensors into one
    """
    print("\ncombining magneto sensor data from bag file topic csv files...")
    # TODO: check if rewrite in assemble_data works with this as is (sub folder structure)
    # TODO: check if csv folder and therefore sensor data exists! Use no_csv_folder list

    for n in range(len(list(filedict.values())[0])):  # loops through number of files
        print("Progress: ", n, "/", len(list(filedict.values())[0]), "\n")
        # contains all data for one run
        run_data_dict = {}

        run = list(filedict.values())[0][n]  # takes the n file of the first topic to get the run number
        #print("\n ---- run: ", run)
        run_number = run.rsplit(os.sep, 1)[1]
        run_number = run_number.split("_", 1)[0]
        print("run number: {}".format(run_number))

        columnnames = []
        for topic in list(filedict.keys()):     # iterates through the individual topics of interest i.e. force, imu...
            # TODO: check order of loops and that run_data_dict actually contains all topics from 1 run
            #print("TOPIC: {} ".format(topic), "of topics: {}".format(list(filedict.keys())))

            # read the file of the current run, which belongs to topic
            file = [f for f in filedict[topic] if run_number in f][0]
            print(f"topic: {topic}, \nfile: {file}")
            data = pd.read_csv(file)

            # count rows:
            data_rows_count = data.shape[0]

            # drop empty rows in df:
            data.dropna(axis=0)

            # creates a new empty dict which is filled with the subtopics, e.g. force_x, force_y, force_z for topic force
            sub_topic_dict = {}
            for item in range(len(magneto_columnnames_dict[topic])):
                # print("item: ", item)
                columnname = list(magneto_columnnames_dict[topic].keys())[item]
                # print("columnname: ", columnname)
                sub_topic_dict[columnname] = data.iloc[:, list(magneto_columnnames_dict[topic].values())[item]].values
            # print("subtopic dict: ", sub_topic_dict)

            run_data_dict[topic] = sub_topic_dict

        # print("run_data_dict: \n", "{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in run_data_dict.items()) + "}")

        # save run_data_dict:
        filename = run_number + "_assembled"
        # convert dict to data frame:
        # determine the longest column in run_data_dict.values() use that for df
        old_max_length = 0
        for topic in list(run_data_dict.values()):  # list of dicts with the subtopics
            for subname, subtopic in topic.items():  # list with data for every subtopic
                # print("subname: ", subname, "\nsubtopic: ", subtopic)
                columnnames.append(subname)

                # print("old_max_length: ", old_max_length)
                max_length = len(subtopic)
                if old_max_length > max_length:
                    max_length = old_max_length
                old_max_length = max_length
        # print("max_length: ", max_length)

        # print("columnnames: ", columnnames)
        run_data_df = pd.DataFrame(columns=columnnames, index=range(max_length))
        print("run_data_df: \n", run_data_df.head())

        for m in range(max_length):
            # print("m: ", m)
            new_row = []
            for subdict in list(run_data_dict.values()):
                for subtopic, subvalues in subdict.items():
                    if len(subvalues) > m:
                        new_row.append(subvalues[m])
                    else:
                        new_row.append(np.nan)
            # print("new_row: ", new_row)
            run_data_df.loc[m] = new_row
        # print("run_data_df: ", run_data_df)

        run_data_df.to_csv(os.path.join(path, "{}.csv".format(filename)), index=True, header=True)

        magneto_raw_dict[run_number] = run_data_dict
    # print("\n\n------------------------------\n\n",
    #       "magneto_raw_dict: \n", "{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in magneto_raw_dict.items()) + "}")

    print("Done! Combining sensor data complete")
    return


def interpolate_data(path):
    """
    CURRENTLY NOT USED
    force, imu, and foot position data was sampled in different frequencies.
    Reduce data points of force data to same length of foot position data points.
    :return:
    """
    from glob import glob
    from scipy.interpolate import interp1d
    import matplotlib.pyplot as plt

    filelist = []
    for file in glob(os.path.join(path, "*.csv")):
        filelist.append(file)

    # filter for "_assembled" in filename:
    filelist = [file for file in filelist if "_assembled_meta" in file]

    # add interpolated force columns
    for file in filelist:
        data = pd.read_csv(file)

        run_number = file.rsplit(os.sep, 1)[1]
        run_number = run_number.split("_", 1)[0]

        filename = run_number + "_assembled_interp"
        #TODO: fix reduction of data point. Currently lost shape, seems to only take start data
        sensorfoot = data['sensorfoot'][1]
        length_of_foot_pos_data = data[f'{sensorfoot}_pos_x'].count()
        length_of_force_data = data['force_x'].count()
        xnew = np.linspace(0, length_of_foot_pos_data, num=length_of_foot_pos_data, endpoint=True)
        f_force_x = interp1d(range(length_of_force_data), data['force_x'])
        f_force_y = interp1d(range(length_of_force_data), data['force_y'])
        f_force_z = interp1d(range(length_of_force_data), data['force_z'])
        ynew_force_x = list(f_force_x(xnew))
        ynew_force_y = list(f_force_y(xnew))
        ynew_force_z = list(f_force_z(xnew))

        #print("interpolated z force: ", ynew_force_z)

        nan_list = [np.nan]*(length_of_force_data - len(ynew_force_z))


        data["interp_force_x"] = ynew_force_x + (nan_list)
        data["interp_force_y"] = ynew_force_y + (nan_list)
        data["interp_force_z"] = ynew_force_z + (nan_list)
        #print(data.head())

        data.to_csv(os.path.join(path, "{}.csv".format(filename)), index=False, header=True)

    return

### Main function in this module:
def magneto_data_assembly(filedict, df_trial_notes, date, no_csv_list, data_folder_path):
    """
    filedict: contains paths to csv files for all runs for a trial sorted by topic.
    df_trial_notes: data frame of the dataCollectionTable.xlsx file.
    no_csv_list: contains list of trial folders, which do not hae csv folder containing converted bag file topics,
        these trials will be ignored for further analysis for now.
    """

    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions

    print("\n ------- magneto data assembly:")
    print("\n")

    # generate folder structure for result files:
    # currently this folder is in the git folder "...python_force_analysis/result_files/YYYY-MM-DD
    result_path = os.path.join(os.getcwd(), "result_files")
    auxiliaryfunctions.attempttomakefolder(result_path)
    result_trial_path = os.path.join(result_path, date)
    auxiliaryfunctions.attempttomakefolder(result_trial_path)

    print(f"Creating folder: {result_trial_path}")

    # assembled_csv folder currently gets created in the respective trial date folder (e.g. 2021-03-23)
    result_trial_assembly_path = os.path.join(result_trial_path, "assembled_csv")
    if os.path.isdir(result_trial_assembly_path):
        assembled_filelist = glob(os.path.join(result_trial_assembly_path, "*_assembled.csv"))
        print(f"folder: {result_trial_assembly_path}, already exists, containing {len(assembled_filelist)} files:")
        for item in assembled_filelist:
            print(f"    - {item}")
    else:
        auxiliaryfunctions.attempttomakefolder(result_trial_assembly_path)
        assembled_filelist = glob(os.path.join(result_trial_assembly_path, "*_assembled.csv")) # should return empty list
        print(f"Creating folder: {result_trial_assembly_path}")

    """ this is for some old magneto data (from Oct 28 2020 I think)
    # TODO rename files to add run number given on time of data collection + trial notes
    run_number_runs = [run for run in list(run_info.keys())]
    
    """
    num_trial_folders = len(glob(os.path.join(data_folder_path, f"{date}*")))
    print(f"length of assembled filelist: {len(assembled_filelist)} | num_trial folders: {num_trial_folders}")

    if len(assembled_filelist) != num_trial_folders:
        # assemble magneto sensor data from individual csv files of bag file topics if number of csv files "*_assembled" is unequal to the number of trials for the selected date
        # otherwise skip this step (for debugging now)
        fill_file_data(filedict, result_trial_assembly_path)

    # use this function to use the dataCollectionTable for the current run analysed.
    # this f combines the _assembled file with the trial notes
    fill_trial_note_data_from_file(result_trial_assembly_path, df_trial_notes)

    """
    # TODO: fix using the pop up window to ask user if they want to overwrite - for now just use YES
    else:
        # using pop up window class defined in auxiliaryfunctions to ask user if they want to overwrite existing csv files
        msg = f"Do you want to overwrite {len(assembled_filelist)} existing _assembled.csv files?"
        root = auxiliaryfunctions.MessageBox()  # init class instance
        # TODO: user button click not returned yet!
        # TODO: multiple windows get initialised and not destroyed!
        res_overwrite = root.popupmsgyesno(msg=msg)     # create message Box and get return value of button clicked
        root.destroy()
        print(f"\nuser's choice - overwrite: {root.get(res_overwrite)}")
        if res_overwrite == "yes":
            print("overwriting csv files...")
            fill_file_data(filedict, result_trial_assembly_path)
            # use this function to use the dataCollectionTable for the current run analysed.
            fill_trial_note_data_from_file(result_trial_assembly_path, df_trial_notes)
        else:
            print("exiting...")
            exit()
    """

    return
