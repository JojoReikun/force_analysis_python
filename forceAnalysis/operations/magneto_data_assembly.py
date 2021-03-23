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


def fill_trial_note_data(path, run_number_runs, df_trial_notes):
    """
    this function fills in the run specific data from the notes, e.g. velocity, sensorfoot etc.
    and adds these information to the run file
    :return:
    """
    # TODO: rewrite to match the new trial note data

    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions
    from glob import glob

    print("\nfilling in >static< trial data...")

    pd.set_option('max_columns', None)

    filelist = []
    for file in glob(os.path.join(path, "*.csv")):
        filelist.append(file)

    # filter for "_assembled" in filename:
    filelist = [file for file in filelist if "_assembled" in file]

    #print("filelist: ", filelist)

    # read in files one by one and add trial notes to dataframe:
    for i, file in enumerate(filelist):
        print("Progress: ", i, "/", len(filelist))
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
        filename = run_number + "_assembled"
        data.to_csv(os.path.join(path, "{}.csv".format(filename)), index=False, header=True)

    return


def fill_file_data(filedict, path):
    """
    reads in file by file (run) and adds data to run_data_dict.
    Returns the path these files are saved to.
    """
    print("\nfilling in file data ...")
    # TODO: check if rewrite in assemble_data works with this as is (subfolder structure)

    for n in range(len(list(filedict.values())[0])):  # loops through number of files
        print("Progress: ", n, "/", len(list(filedict.values())[0]), "\n")
        # contains all data for one run
        run_data_dict = {}

        run = list(filedict.values())[0][n]  # takes the n file of the first topic to get the run number
        #print("\n ---- run: ", run)
        run_number = run.rsplit(os.sep, 1)[1]
        run_number = run_number.split("_", 1)[0]
        #print("run number: {}".format(run_number))

        columnnames = []
        for topic in list(filedict.keys()):
            # TODO: check order of loops and that run_data_dict actually contains all topics from 1 run
            print("TOPIC: {} ".format(topic), "of topics: {}".format(list(filedict.keys())))

            # read the file of the current run, which belongs to topic
            # instead of using n make sure the file fits the run number
            file = [f for f in filedict[topic] if run_number in f][0]
            #print("file: ", file)

            data = pd.read_csv(file)

            # count rows: data_rows_count = data.shape[0]

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
        # print("run_data_df: \n", run_data_df)

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
    return


def interpolate_data(path):
    """
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
    filelist = [file for file in filelist if "_assembled" in file]

    # add interpolated force columns
    for file in filelist:
        data = pd.read_csv(file)

        run_number = file.rsplit(os.sep, 1)[1]
        run_number = run_number.split("_", 1)[0]

        filename = run_number + "_assembled"
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


def create_summary_file(path, run_number_runs, path_summary):
    # TODO: put this into seperate python file
    """
        this function fills in the run specific data from the notes, e.g. velocity, sensorfoot etc.
        and adds these information to the run file
        :return:
        """
    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions
    from glob import glob
    print("creating summary files ... ")
    pd.set_option('max_columns', None)

    filelist = []
    for file in glob(os.path.join(path, "*.csv")):
        filelist.append(file)

    # filter for "_assembled" in filename:
    filelist = [file for file in filelist if "_assembled" in file]

    # create summary data frame:
    summarycolumns = ['run', 'velocity', 'step_frequency', 'footfallpattern', 'direction', 'surface', 'sensorfoot',
                      'failedstep', 'failedfoot', 'failreason', 'forcesbiased',
                      'max_force_x', 'max_force_y', 'max_force_z', 'mean_force_x', 'mean_force_y', 'mean_force_z',
                      'min_force_x', 'min_force_y', 'min_force_z']
    summary_data = pd.DataFrame(columns=summarycolumns, index=range(len(filelist)))

    # read in files one by one and add trial notes to dataframe:
    i = 1
    file = filelist[i]
    for i, file in zip(range(len(filelist)), filelist):
        print(f"Progress: {i}/{len(filelist)}")
        run_number = file.rsplit(os.sep, 1)[1]
        run_number = run_number.split("_", 1)[0]
        #print("\n--- run: ", run_number)

        data = pd.read_csv(file)

        summary_data['run'][i] = run_number
        summary_data['max_force_x'][i] = np.mean(sorted(list(data['force_x']), reverse=True)[0:3])
        summary_data['max_force_y'][i] = np.mean(sorted(list(data['force_y']), reverse=True)[0:3])
        summary_data['max_force_z'][i] = np.mean(sorted(list(data['force_z']), reverse=True)[0:3])
        summary_data['mean_force_x'][i] = np.mean(data['force_x'])
        summary_data['mean_force_y'][i] = np.mean(data['force_y'])
        summary_data['mean_force_z'][i] = np.mean(data['force_z'])
        summary_data['min_force_x'][i] = np.mean(sorted(list(data['force_x']), reverse=False)[0:3])
        summary_data['min_force_y'][i] = np.mean(sorted(list(data['force_y']), reverse=False)[0:3])
        summary_data['min_force_z'][i] = np.mean(sorted(list(data['force_z']), reverse=False)[0:3])


        if run_number in run_number_runs:
            # get summary values:

            summary_data['velocity'][i] = data['velocity'][1]
            summary_data['step_frequency'][i] = data['step_frequency'][1]
            summary_data['footfallpattern'][i] = data['footfallpattern'][1]
            summary_data['direction'][i] = data['direction'][1]
            summary_data['surface'][i] = data['surface'][1]
            summary_data['sensorfoot'][i] = data['sensorfoot'][1]
            summary_data['failedstep'][i] = data['failedstep'][1]
            summary_data['failedfoot'][i] = data['failedfoot'][1]
            summary_data['failreason'][i] = data['failreason'][1]
            summary_data['forcesbiased'][i] = data['forcesbiased'][1]
            summary_data['max_force_x'][i] = np.mean(sorted(list(data['force_x']))[-3])
            summary_data['max_force_y'][i] = np.mean(sorted(list(data['force_y']))[-3])
            summary_data['max_force_z'][i] = np.mean(sorted(list(data['force_z']))[-3])


    #print("\n", summary_data)

    #save summary data:
    summary_data.to_csv(os.path.join(path_summary, "summary_data.csv"))

    return


### Main function in this module:
def magneto_data_assembly(filedict, overwrite_csv_files, df_trial_notes):
    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions
    print("\nmagneto data assembly")

    path = os.path.join(os.getcwd(), "assembled_csv")
    auxiliaryfunctions.attempttomakefolder(path)

    path_summary = os.path.join(path, "summary_data")
    auxiliaryfunctions.attempttomakefolder(path_summary)

    # TODO rename files to add run number given on time of data collection + trial notes

    run_number_runs = [run for run in list(run_info.keys())]

    if overwrite_csv_files == True:
        # only read in files and assemble data if overwrite is True
        fill_file_data(filedict, path)
        if os.listdir(path) != []:
            fill_trial_note_data(path, run_number_runs, df_trial_notes)
        else:
            print("No files in assembled folder. Maybe set overwrite csv files to True?")
            exit()

    if os.listdir(path) != []:
        create_summary_file(path, run_number_runs, path_summary)
        #interpolate_data(path)

    return
