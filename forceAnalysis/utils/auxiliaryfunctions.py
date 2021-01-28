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
# TODO: put this onto plot_force_and_position
def find_all_max_and_min_of_function(x_values, y_foot_smoothed, run_number):
    import numpy as np
    from scipy.signal import find_peaks
    import pandas as pd

    print("\nmax and mins...")

    dy = np.diff(y_foot_smoothed)
    peaks, _ = find_peaks(y_foot_smoothed)
    peaks = [peak for peak in peaks]
    #print("peaks: ", peaks)

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
    # if moving average of 1000 y values moves more than certain amount, include maximum:
    ### OLD:
    # df_extrema_three_max = df_extrema[df_extrema['y'] >= min(three_max_y)]
    # df_extrema_filtered = df_extrema[df_extrema['x'] >= min(df_extrema_three_max['x'])]

    ### NEW:
    avg_window_length = 15
    moving_average = []
    keepers = []

    #get the differences between subsequent frames in y_foot_smoothed:
    differences = [m - n for n, m in zip(y_foot_smoothed, y_foot_smoothed[1:])]
    # print("len(y_foot_smoothed): ", len(y_foot_smoothed), "len(differences): ", len(differences))
    # create a moving average
    scalefactor = define_scalefactor()
    for i in range(1, len(differences)):
        if i <= len(y_foot_smoothed-avg_window_length):
            moving_average = scalefactor * np.mean(np.abs(differences[i:(i + avg_window_length)]))
        else:
            moving_average = np.mean(np.abs(differences[len(differences)-avg_window_length:len(differences)]))
        if i in peaks and moving_average > 10.0:
            keepers.append(i)
    keepers_diff = list(np.diff(keepers))
    print("keepers: ", keepers, "len: ", len(keepers))
    keepers_diff.append(1000)  # add a high value to make next filter step work
    print("keepers diff: ", keepers_diff, "len: ", len(keepers_diff))


    # look for multiple maxima close together resulting from remaining noise in smoothing
    keepers2 = [keeper for i, keeper in enumerate(keepers) if keepers_diff[i] > 32]
    print("keepers2: ", keepers2, "len: ", len(keepers2))

    df_extrema_filtered = df_extrema[df_extrema['index'].isin(keepers2)]

    #print(df_extrema_filtered)

    return df_extrema, df_extrema_filtered, keepers2, three_max_y


# TODO: put this onto plot_force_and_position
def find_step_intervals(df_extrema, df_extrema_filtered, y_foot_smoothed, keepers2, three_max):
    """
    swing phase is defined as the minimum before the highest max of the step cycle of the foot, if there are more than 3 maxima.
    stance phase is then from the highest maximum in the step cycle to the next minimum before the following next highest peak.
    :return: tuple with 2 lists containing the start and end index for swing and stance phase respectively.
    """
    import numpy as np

    print(f"\ndetecting step intervals ...")
    # check if three_max are close to each other
    max_max = max(three_max)
    three_max_keepers = [m for m in three_max if (m >= max_max-7.0)]
    print("filter maxima... old, new: ", three_max, three_max_keepers)

    # get the indices of the three maxima to see which one is the first
    rounder = 2
    indices_three_max = []
    #print(round(df_extrema_filtered['y'], rounder))
    for m in three_max_keepers:
        # TODO: FIX! through rounding the same condition applies to multiple values, hence intervals are found double
        print(round(m, rounder))
        row_m = df_extrema_filtered[round(df_extrema_filtered['y'], rounder) == round(m, rounder)]
        if row_m.shape[0] != 0:
            indices_three_max.append(row_m['index'].values[0])
    indices_three_max = sorted(indices_three_max, reverse=False)    # sort indices of three max from low to high

    print("indices three max: ", indices_three_max)

    swings = []
    if len(indices_three_max) > 0:
        p_last = 0
        for i, p in enumerate(indices_three_max):
            #p = df_extrema[df_extrema['index'] == p].index[0]
            print("i: ", i, "  p: ", p)
            if p == p_last:
                break
            else:
                # if there is no other maximum before the first of the highest...
                if i == 0 and indices_three_max[0] == keepers2[0]:
                    print("there is no other maximum before the first of the highest")
                    low_window = list(y_foot_smoothed[:p])    # get all values before the first highest max
                    lowest = low_window.index(min(low_window))
                    print("lowest: ", lowest)
                    swings.append([lowest, p])
                elif i == 0 and indices_three_max[0] != keepers2[0]:
                    print("there is another maximum before p")
                    start_index = keepers2[list(keepers2).index(p) - 1]
                    print("start index: ", start_index, "  end index: ", p)
                    low_window = list(
                        y_foot_smoothed[start_index:p])  # get all values betw. the p highest max to the next max before
                    print(len(low_window))
                    lowest = start_index + low_window.index(min(low_window))
                    print("lowest: ", lowest)
                    swings.append([lowest, p])
                elif 0 < i <= len(indices_three_max):
                    print("there is another maximum before p")
                    start_index = keepers2[list(keepers2).index(p)-1]
                    print("start index: ", start_index, "  end index: ", p)
                    low_window = list(y_foot_smoothed[start_index:p])  # get all values betw. the p highest max to the next max before
                    print(len(low_window))
                    lowest = start_index + low_window.index(min(low_window))
                    print("lowest: ", lowest)
                    swings.append([lowest, p])
                elif i == len(indices_three_max) and i <= 3:
                    swings.append([np.nan, np.nan])
            p_last = p
    else:
        print("no maxima found!")
        swings = [[np.nan, np.nan],
                  [np.nan, np.nan],
                  [np.nan, np.nan]]

    # For now doubles in swing phases due to rounding above will just be removed:
    # TODO: Fix this issue to not loose steps
    swings2 = []
    swings2 = [x for x in swings if x not in swings2]

    print("swings: ", swings)

    return swings2


# TODO: put this onto plot_force_and_position
def find_inflection_point_before_highest_max(x_values, y_foot_smoothed, df_extrema_filtered):
    import numpy as np

    # constrain foot_smoothed to the area between highest max and the max before:
    row_highest_max = df_extrema_filtered[df_extrema_filtered['y'] == max(df_extrema_filtered['y'])]
    index_highest_max = row_highest_max.index
    #print("INDEX first row, col1: ", df_extrema_filtered.iloc[0, 0])
    #print("INDEX row highest max: ", df_extrema_filtered.loc[index_highest_max, 'index'].values[0])

    if df_extrema_filtered.loc[index_highest_max, 'index'].values[0] == df_extrema_filtered.iloc[0, 0]:
        index1 = 0
    else:
        row_before_highest_max = df_extrema_filtered.loc[index_highest_max-1, :]
        index1 = row_before_highest_max['index'].values[0]
    index2 = row_highest_max['index'].values[0]

    y_foot_smoothed_constrained = y_foot_smoothed[index1 : index2]
    #print(len(y_foot_smoothed), len(y_foot_smoothed_constrained))

    df_prime = np.gradient(y_foot_smoothed_constrained)     # first deriv
    f_prime = np.gradient(df_prime)                         # second deriv
    #print(f_prime)
    indices = np.where(np.diff(np.sign(f_prime)))[0]   # get indices of where the sign switches
    if len(indices) > 0:
        #print(indices)
        i = -1
        inflections_x = x_values[index1 + indices[i]]
        # checks if distance between the highest position data and the inflection point is very close -> leftover peak from smoothing
        diff_infl_max = (x_values[index2]-inflections_x)/100000
        #print("Distance between max and inflection point: ", diff_infl_max)
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


def define_scalefactor():
    scalefactor = 500
    return scalefactor