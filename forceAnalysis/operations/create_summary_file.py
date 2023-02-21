import pandas as pd
import os
import numpy as np


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
    filelist = [file for file in filelist if "_assembled_meta" in file]

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


def create_summary_file2(path, path_summary, date):
    """
    use this function for the Magneto@USC data collection
    """
    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions
    from glob import glob
    print("\n -- creating summary files (2)... \n")
    pd.set_option('max_columns', None)

    filelist = []
    for file in glob(os.path.join(path, "*.csv")):
        filelist.append(file)

    # filter for "_assembled" in filename:
    filelist = [file for file in filelist if "_assembled_meta" in file]
    print("filelist for summary data: ", filelist)

    if filelist == []:
        print("no fully assembled files found [>>*assembled_meta.csv<<], run forceAnalysis.assemble() first.")
        exit()

    # create summary data frame:
    summarycolumns = ['date_time', 'run', 'gait', 'velocity', 'step_frequency', 'bodyheight', 'direction', 'surface', 'sensorfoot',
                      'failed', 'failedfoot', 'comments', 'forces_gamma_collected', 'climbed_time', 'climbed_distance',
                      'max_force_x', 'max_force_y', 'max_force_z', 'mean_force_x', 'mean_force_y', 'mean_force_z',
                      'min_force_x', 'min_force_y', 'min_force_z']
    summary_data = pd.DataFrame(columns=summarycolumns, index=range(len(filelist)))

    # read in files one by one and add trial notes to dataframe:
    i = 1
    file = filelist[i]
    for i, file in zip(range(len(filelist)), filelist):
        print(f"Progress: {i}/{len(filelist)}")

        data = pd.read_csv(file)
        # print(data.head())

        summary_data['date_time'] = data['date_time'][1]
        summary_data['run'][i] = data['run'][1]
        summary_data['gait'][i] = data['gait'][1]
        summary_data['velocity'][i] = data['velocity'][1]
        summary_data['step_frequency'][i] = data['step_frequency'][1]
        summary_data['bodyheight'][i] = data['bodyheight_from_handle'][1]
        summary_data['direction'][i] = data['direction'][1]
        summary_data['surface'][i] = data['surface'][1]
        summary_data['sensorfoot'][i] = data['sensorfoot'][1]
        summary_data['failed'][i] = data['failed'][1]
        summary_data['failedfoot'][i] = data['failedfoot'][1]
        summary_data['comments'][i] = data['comments'][1]
        summary_data['forces_gamma_collected'][i] = data['forces_gamma_collected'][1]

        summary_data['climbed_time'][i] = data['climbed_time'][1]
        summary_data['climbed_distance'][i] = data['climbed_distance'][1]
        #summary_data['speed'][i] = float(data['climbed_distance'][1])/float(data['climbed_time'][1])

        summary_data['max_force_x'][i] = np.mean(sorted(list(data['force_x']), reverse=True)[0:3])
        summary_data['max_force_y'][i] = np.mean(sorted(list(data['force_y']), reverse=True)[0:3])
        summary_data['max_force_z'][i] = np.mean(sorted(list(data['force_z']), reverse=True)[0:3])
        summary_data['mean_force_x'][i] = np.mean(data['force_x'])
        summary_data['mean_force_y'][i] = np.mean(data['force_y'])
        summary_data['mean_force_z'][i] = np.mean(data['force_z'])
        summary_data['min_force_x'][i] = np.mean(sorted(list(data['force_x']), reverse=False)[0:3])
        summary_data['min_force_y'][i] = np.mean(sorted(list(data['force_y']), reverse=False)[0:3])
        summary_data['min_force_z'][i] = np.mean(sorted(list(data['force_z']), reverse=False)[0:3])

    print("\n", summary_data)

    # save summary data:
    summary_data.to_csv(os.path.join(path_summary, f"{date}_summary_data.csv"))
    return


def create_summary(date):
    from forceAnalysis.utils import auxiliaryfunctions

    result_path = os.path.join(os.getcwd(), "result_files")
    result_trial_path = os.path.join(result_path, date)
    result_trial_assembly_path = os.path.join(result_trial_path, "assembled_csv")

    path_summary = os.path.join(result_trial_path, "summary_data")
    auxiliaryfunctions.attempttomakefolder(path_summary)

    files_in_dir = os.listdir(result_trial_assembly_path)
    files_meta = [file for file in files_in_dir if "meta" in file]
    if  files_meta != []:
        # use this function if analysing the 28-10-2020 data collection:
        #create_summary_file(result_trial_assembly_path, run_number_runs, path_summary)

        # use this function to use data from Magneto@USC data collection Mar/Apr 2021:
        # files needed for summary data contain the ending: "*assembled_meta.csv"
        create_summary_file2(result_trial_assembly_path, path_summary, date)

    # TODO: puts multiple entries in cell?? Look at summary_data.csv and fix ?? old comment --> check

    return