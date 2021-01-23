def get_path_of_folder():
    ### IMPORTS
    import os
    from tkinter import filedialog, Tk

    root = Tk()


    current_path = os.getcwd()
    folder_path = filedialog.askdirectory(parent=root, initialdir=current_path,
                                          title="Please select folder with data csv files")
    root.withdraw()  # to hide tkinter window
    return folder_path


def define_colours():
    colour_dict = {'fore-aft': "#548235",   # green
                   'lateral': "#7030A0",    # purple
                   'normal': "#BF9000"}     # sand
    return colour_dict


def attempttomakefolder(foldername, recursive=False):
    ''' Attempts to create a folder with specified name. Does nothing if it already exists. '''
    import os
    try:
        os.path.isdir(foldername)
    except TypeError: #https://www.python.org/dev/peps/pep-0519/
        foldername=os.fspath(foldername) #https://github.com/AlexEMG/DeepLabCut/issues/105 (windows)

    if os.path.isdir(foldername):
        #print(foldername, " already exists!")
        pass
    else:
        if recursive:
            os.makedirs(foldername)
        else:
            os.mkdir(foldername)


def get_sensorfoot_for_run(run_number):
    "takes a string containing the run number and returns the respective sensorfoot for this run"
    sensorfoot_dict = {(1, 16):"FR",
                       (16, 34):"HR"}

    #print("run number: ", run_number, type(run_number))
    # extract the run number from the string:
    run_int = int(''.join(filter(lambda i: i.isdigit(), run_number)))
    #print("run_int: ", run_int, type(run_int))

    sensorfoot_of_run = 0
    for i in range(len(sensorfoot_dict.keys())):
        key = list(sensorfoot_dict.keys())[i]
        if run_int in range(key[0], key[1]):
            sensorfoot_of_run = sensorfoot_dict[key]

    if sensorfoot_of_run == 0:
        print("Run number has no responding sensorfoot")

    #print("aux funcs, sensorfoot: ", sensorfoot_of_run)
    return sensorfoot_of_run


# the indices of these points in the data will be needed, --> return lists of points
def find_all_max_and_min_of_function(x_values, y_foot_smoothed):
    import numpy as np
    from scipy.signal import find_peaks
    import matplotlib.pyplot as plt
    import seaborn as sn
    import pandas as pd

    plt.figure()

    print("max and mins...")

    dy = np.diff(y_foot_smoothed)
    peaks, _ = find_peaks(y_foot_smoothed)
    peaks = [peak for peak in peaks]
    #print("peaks: ", peaks)

    sn.lineplot(x_values, y_foot_smoothed)
    extrema = {"index": [],
               "x": [],
               "y": []}
    for i in peaks:
        extrema["index"].append(i)
        extrema["x"].append(x_values[i])
        extrema["y"].append(y_foot_smoothed[i])

    three_max_y = sorted(extrema['y'], reverse=True)[:3]
    print(three_max_y)

    df_extrema = pd.DataFrame(extrema)

    # remove "standing extrema":
    df_extrema_three_max = df_extrema[df_extrema['y'] >= min(three_max_y)]
    df_extrema_filtered = df_extrema[df_extrema['x'] >= min(df_extrema_three_max['x'])]
    #df_extrema_filtered = pd.concat([df_extrema_filtered_1, df_extrema_filtered_2])
    #print(df_extrema_filtered)

    # testplot
    # sn.scatterplot(x='x', y='y', data=df_extrema)
    # sn.scatterplot(x='x', y='y', data=df_extrema_filtered, color='red')
    # sn.scatterplot(x='x', y='y', data=df_extrema_filtered[df_extrema_filtered['y']==max(three_max_y)], color='green')
    # plt.show()

    return df_extrema_filtered


def find_inflection_point_before_highest_max(x_values, y_foot_smoothed, df_extrema_filtered):
    import numpy as np

    # constrain foot_smoothed to the area between highest max and the max before:
    row_highest_max = df_extrema_filtered[df_extrema_filtered['y'] == max(df_extrema_filtered['y'])]
    index_highest_max = row_highest_max.index
    print("INDEX first row, col1: ", df_extrema_filtered.iloc[0, 0])
    print("INDEX row highest max: ", df_extrema_filtered.loc[index_highest_max, 'index'].values[0])

    if df_extrema_filtered.loc[index_highest_max, 'index'].values[0] == df_extrema_filtered.iloc[0, 0]:
        index1 = 0
    else:
        row_before_highest_max = df_extrema_filtered.loc[index_highest_max-1, :]
        index1 = row_before_highest_max['index'].values[0]
    index2 = row_highest_max['index'].values[0]

    y_foot_smoothed_constrained = y_foot_smoothed[index1 : index2]
    print(len(y_foot_smoothed), len(y_foot_smoothed_constrained))

    df_prime = np.gradient(y_foot_smoothed_constrained)     # first deriv
    f_prime = np.gradient(df_prime)                         # second deriv
    #print(f_prime)
    indices = np.where(np.diff(np.sign(f_prime)))[0]   # get indices of where the sign switches
    if len(indices) > 0:
        print(indices)
        i = -1
        inflections_x = x_values[index1 + indices[i]]
        # checks if distance between the highest position data and the inflection point is very close -> leftover peak from smoothing
        diff_infl_max = (x_values[index2]-inflections_x)/100000
        print("Distance between max and inflection point: ", diff_infl_max)
        # if distance is too close, the inflection point before is taken
        if diff_infl_max < 500:
            print("updating index for inflection point")
            i = -2
        inflections_x = x_values[index1 + indices[i]]
        inflections_y = y_foot_smoothed_constrained[indices[i]]

        print("inflection point: ", inflections_x, inflections_y)

        return (inflections_x, inflections_y)

    else:
        print("no inflection points found...")
        return (np.nan, np.nan)


def find_closest_value(list, value):
    """
    finds the closest value in a list to a given value
    :param list: list of values where to look for the closest
    :param value: value
    :return: closest value to value of list
    """

    return list[min(range(len(list)), key=lambda i: abs(list[i]-value))]