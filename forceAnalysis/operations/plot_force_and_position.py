def get_neutral_force_z(foot_smoothed, x_values, data_forces_and_pos, run_number, df_extrema_filtered):
    """
    This function is used on the smoothed foot data.
    This function looks for the time when the sensorfoot is in the air (highest position spike = global max).
    It then looks for the steepest slope before the global max.
    Around that index 10 values are taken from the force_z data, to get an estimate of the "neutral" force_z.
    :return:
    df_extrema_filtered: contains the indices, the x and y values of the maxima and minima of the smoothed foot function
    neutral_force_z
    """
    ### IMPORTS:
    from forceAnalysis.utils import auxiliaryfunctions
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sn

    print("determining neutral force z...")

    # find the inflection point before the global max, returns tuple of coords of inflection point
    inflection_point = auxiliaryfunctions.find_inflection_point_before_highest_max(x_values, foot_smoothed, df_extrema_filtered)

    # get 10 values around the inflection point of the z force:
    # first find the closest x-value of the force to the interception point:
    closest_forceZ = auxiliaryfunctions.find_closest_value(list(data_forces_and_pos['force_timestamp']), inflection_point[0])
    index_of_closest = list(data_forces_and_pos[data_forces_and_pos['force_timestamp'] == closest_forceZ].index)

    neutral_force_subset = data_forces_and_pos.loc[index_of_closest[0]-5:index_of_closest[0]+5, :]
    neutral_force_mean = np.mean(list(neutral_force_subset['force_z']))
    neutral_force_std = np.std(list(neutral_force_subset['force_z']))
    print("number_of_forces: ", neutral_force_subset.shape[0], "\nmean: ", neutral_force_mean, "\nstd: ", neutral_force_std)

    return inflection_point, neutral_force_mean, neutral_force_std


def smooth_foot_position(foot_pos_x, foot_timestamp, sample_spacing_foot, df_current_run_summary, filtertype):
    """
    takes the values for the x-position data of the sensorfoot and smoothes them using Savitzky-Golay filter
    or the butterworth low-pass filter
    filter: "savgol" or "butter"
    """
    ### IMPORTS:
    from scipy import signal
    from scipy import fft, ifft
    import matplotlib.pyplot as plt
    import numpy as np

    print("smoothing...")

    x_values = list(foot_timestamp)
    if filtertype == "savgol":
        y_values_savgol = signal.savgol_filter(foot_pos_x, 121, 3)  # windowlength, filterorder
        return x_values, y_values_savgol
    elif filtertype == "fft":
        n = len(foot_timestamp)
        fourier = fft(foot_pos_x)
        freq = fft.fftfreq(n, d=sample_spacing_foot)
        # Find the peak frequency: we can focus on only the positive frequencies
        power = np.abs(freq)**2
        pos_mask = np.where(freq > 0)
        freqs = freq[pos_mask]
        peak_freq = freqs[power[pos_mask].argmax()]
        print("peak_freq: ", peak_freq)
        high_freq_fft = fourier.copy()
        high_freq_fft[np.abs(freq) > peak_freq] = 0
        print("len(high_freq_fft): ", len(high_freq_fft))
        y_values_fft = fft.ifft(high_freq_fft)
        # Testplotting:
        # plt.figure()
        # plt.plot(freq, np.abs(fourier))
        # plt.show()
        # plt.clf()
        # plt.close()
        return x_values, np.abs(y_values_fft)
    elif filtertype == "butter":
        # adjust the frequency of the filter based on the velocity and step frequency of the run:
        frequency = 0.001
        velocity = df_current_run_summary['velocity']
        step_freq = df_current_run_summary['step_frequency']
        multiplier = 2./(velocity*step_freq)
        print("velocity, step_frequency, multiplier: \n", velocity, "\n" ,step_freq, "\n" , multiplier)
        # smooth
        b, a = signal.butter(3, frequency*multiplier, btype="lowpass", analog=False)
        y_values_butter = signal.filtfilt(b, a, foot_pos_x)
        return x_values, y_values_butter


def plot_force_data_and_position_data(overwrite_plots, smoothing, filtertype):
    import matplotlib.pyplot as plt
    import seaborn as sn
    import pandas as pd
    import os.path
    import numpy as np
    from glob import glob
    from forceAnalysis.utils import auxiliaryfunctions

    feet = ['FR', 'FL', 'HR', 'HL']

    print("plotting forces and positions...")

    if overwrite_plots == True:
        path = os.path.join(os.getcwd(), "assembled_csv")
        summary_path = os.path.join(path, "summary_data")

        output_path = os.path.join(path, "force_and_position_plots")
        output_path2 = os.path.join(output_path, "foot_plots")
        auxiliaryfunctions.attempttomakefolder(output_path)
        auxiliaryfunctions.attempttomakefolder(output_path2)

        if os.path.isdir(summary_path):
            summary_data = pd.read_csv(os.path.join(summary_path, "summary_data.csv"))
            data_vel_and_freq = summary_data[['run', 'velocity', 'step_frequency', 'footfallpattern', 'direction', 'surface', 'forcesbiased']]
        else:
            print("no summary_data folder. Run forceAnalysis.assemble() first.")

        if os.path.isdir(path):
            number_of_files = len(glob(os.path.join(path, "*.csv")))
            print("number_of_files = ", number_of_files)

            if number_of_files == 0:
                print("no files in assemble_csv found, run forceAnalysis.assemble() first.")
                exit()

            # create empty dataframe to store swing phase data for all runs:
            all_swing_data = {}

            for i, file in enumerate(glob(os.path.join(path, "*.csv"))):
                print("Progress: ", i, "/", number_of_files)
                # print("file: ", file)

                data = pd.read_csv(file)
                # print(data)
                sensorfoot = data['sensorfoot'][1]
                data_forces_and_pos = data[['force_x', 'force_y', 'force_z', 'FR_pos_x', 'FL_pos_x', 'HR_pos_x', 'HL_pos_x',
                                            'force_timestamp', 'imu_linacc_y', 'imu_timestamp', 'FR_timestamp', 'FL_timestamp',
                                            'HR_timestamp', 'HL_timestamp']]

                #print("data_forces_and_pos: ", data_forces_and_pos.head())

                sample_spacing_foot = data_forces_and_pos['FR_timestamp'][5] - data_forces_and_pos['FR_timestamp'][4]
                sample_spacing_force = data_forces_and_pos['force_timestamp'][5] - data_forces_and_pos['force_timestamp'][4]
                # print("sample freq foot: ", sample_spacing_foot,
                #       "\nsample freq force: ", sample_spacing_force)

                #x_forces = range(data_forces_and_pos['force_x'].count())

                min_x_pos = range(100000)
                for foot in feet:
                    x_pos = range(data_forces_and_pos[f'{foot}_pos_x'].count())
                    if len(x_pos) < len(min_x_pos):
                        min_x_pos = x_pos

                run_number = file.rsplit(os.sep, 1)[1]

                run_number = run_number.split("_", 1)[0]

                # get velocity and step_frequency of current run
                df_current_run_summary = data_vel_and_freq.loc[data_vel_and_freq['run'] == run_number]
                #print(df_current_run_summary)

                print("run number: ", run_number, "\nmin_x_pos: ", len(min_x_pos))

                colours = ['#e3433d', '#0b6ade', '#5bdea5', '#690612', '#150669', '#1c5239']
                sn.set_style('whitegrid')

                scalefactor = auxiliaryfunctions.define_scalefactor()
                FR_pos_x = data_forces_and_pos['FR_pos_x']
                FR_pos_x = [y * scalefactor for y in FR_pos_x]
                FR_pos_x = FR_pos_x[0:len(min_x_pos)]
                FL_pos_x = data_forces_and_pos['FL_pos_x']
                FL_pos_x = [y * scalefactor for y in FL_pos_x]
                FL_pos_x = FL_pos_x[0:len(min_x_pos)]
                HR_pos_x = data_forces_and_pos['HR_pos_x']
                HR_pos_x = [y*scalefactor for y in HR_pos_x]
                HR_pos_x = HR_pos_x[0:len(min_x_pos)]
                HL_pos_x = data_forces_and_pos['HL_pos_x']
                HL_pos_x = [y*scalefactor for y in HL_pos_x]
                HL_pos_x = HL_pos_x[0:len(min_x_pos)]
                shift_value = abs(np.mean(FR_pos_x[:10])) + abs(np.mean(HR_pos_x[:10]))
                HR_pos_x = [y + shift_value for y in HR_pos_x]
                HL_pos_x = [y + shift_value for y in HL_pos_x]
                imu_y = data_forces_and_pos['imu_linacc_y']
                imu_y = [y + np.mean(FR_pos_x[:10]) for y in imu_y]


                #### SMOOTHING
                swing_phases_feet = {}
                for foot in feet:
                    print("\n>>>>> FOOT: ", foot, "\n")
                    # get sensorfoot:
                    sensorfoot_of_run = auxiliaryfunctions.get_sensorfoot_for_run(run_number)
                    print(run_number, sensorfoot_of_run)

                    # smooth foot data
                    if isinstance(foot, str) and foot == "FR":
                        x_values, foot_smoothed = smooth_foot_position(FR_pos_x, data_forces_and_pos['FR_timestamp'][
                                                                                 :len(min_x_pos)], sample_spacing_foot,
                                                                       df_current_run_summary, filtertype=filtertype)
                    elif isinstance(foot, str) and foot == "HR":
                        x_values, foot_smoothed = smooth_foot_position(HR_pos_x, data_forces_and_pos['HR_timestamp'][
                                                                                 :len(min_x_pos)], sample_spacing_foot,
                                                                       df_current_run_summary, filtertype=filtertype)
                    elif isinstance(foot, str) and foot == "FL":
                        x_values, foot_smoothed = smooth_foot_position(FL_pos_x, data_forces_and_pos['FL_timestamp'][
                                                                                 :len(min_x_pos)], sample_spacing_foot,
                                                                       df_current_run_summary, filtertype=filtertype)
                    elif isinstance(foot, str) and foot == "HL":
                        x_values, foot_smoothed = smooth_foot_position(HL_pos_x, data_forces_and_pos['HL_timestamp'][
                                                                                 :len(min_x_pos)], sample_spacing_foot,
                                                                       df_current_run_summary, filtertype=filtertype)

                    # find all maxima of smoothed foot:
                    df_extrema, df_extrema_filtered, keepers2, three_max = auxiliaryfunctions.find_all_max_and_min_of_function(
                        x_values, foot_smoothed, run_number)
                    df_highest_max = df_extrema_filtered[df_extrema_filtered['y'] == max(df_extrema_filtered['y'])]

                    # if the current foot is the sensorfoot, store data for plotting later
                    if foot == sensorfoot_of_run:
                        df_extrema_filtered_sf = df_extrema_filtered
                        df_highest_max_sf = df_highest_max
                        foot_smoothed_sf = foot_smoothed

                    # find all swing phases of smoothed foot:
                    ## find the step intervals:
                    swings = auxiliaryfunctions.find_step_intervals(df_extrema, df_extrema_filtered, foot_smoothed,
                                                                    keepers2, three_max)
                    swing_phases_feet[foot] = swings

                    # TESTPLOTS for individual feet:
                    sn.lineplot(x_values, foot_smoothed, color='grey')
                    sn.scatterplot(x='x', y='y', data=df_extrema, alpha=0.5)
                    sn.scatterplot(x='x', y='y', data=df_extrema_filtered, color='red')
                    sn.scatterplot(x='x', y='y', data=df_extrema_filtered[df_extrema_filtered['y'] == max(three_max)],
                                   color='green')
                    # plot swing phases:
                    for swing in swings:
                        plt.vlines(x_values[swing[0]], ymin=min(foot_smoothed), ymax=max(foot_smoothed), linewidth=0.8)
                        plt.vlines(x_values[swing[1]], ymin=min(foot_smoothed), ymax=max(foot_smoothed), linewidth=0.8)
                    plt.title(run_number + "_" + foot)
                    fig1 = plt.gcf()
                    fig1.savefig(os.path.join(output_path2, f'{run_number}_{foot}.png'), dpi=300)

                    plt.show()

                    if foot == sensorfoot_of_run:
                        # get the neutral z force:
                        inflection_point, neutral_force_mean, neutral_force_std = get_neutral_force_z(
                            foot_smoothed=foot_smoothed, x_values=x_values, data_forces_and_pos=data_forces_and_pos,
                            run_number=run_number, df_extrema_filtered=df_extrema_filtered)





                # swing_phases_feet contains all the swing phases for each foot for the current run
                print("\n\nswing_phases_feet: \n", swing_phases_feet, '\n')


                # Plotting
                fig, ax = plt.subplots()
                #ax2 = ax.twiny()
                # plot imu data:
                sn.lineplot(x = data_forces_and_pos['imu_timestamp'], y = imu_y, color='black', alpha=0.6, linewidth = 1, dashes=(5,5), label='imu linear acc. y')

                # plot forces:
                sn.lineplot(x = data_forces_and_pos['force_timestamp'], y = data_forces_and_pos['force_x'], ax=ax, color=colours[0], label=f'{sensorfoot}_force_x')
                sn.lineplot(x = data_forces_and_pos['force_timestamp'], y = data_forces_and_pos['force_y'], ax=ax, color=colours[1], label=f'{sensorfoot}_force_y')
                sn.lineplot(x = data_forces_and_pos['force_timestamp'], y = data_forces_and_pos['force_z'], ax=ax, color=colours[2], label=f'{sensorfoot}_force_z')

                # plot foot position data:
                sn.lineplot(x = data_forces_and_pos['FR_timestamp'][:len(min_x_pos)], y = FR_pos_x, label='FR', dashes=[(2,2)], linewidth=1)
                sn.lineplot(x = data_forces_and_pos['FL_timestamp'][:len(min_x_pos)], y = FL_pos_x, label='FL', dashes=[(2,2)], linewidth=1)
                sn.lineplot(x = data_forces_and_pos['HL_timestamp'][:len(min_x_pos)], y = HL_pos_x, label='HL', dashes=[(2,2)], linewidth=1)
                sn.lineplot(x = data_forces_and_pos['HR_timestamp'][:len(min_x_pos)], y = HR_pos_x, label='HR', dashes=[(2,2)], linewidth=1)

                if smoothing == True and isinstance(sensorfoot_of_run, str):
                    sn.lineplot(x = x_values, y = foot_smoothed_sf, label=f'{sensorfoot_of_run} pos {filtertype}', linewidth=1)
                    sn.scatterplot(x='x', y='y', data=df_extrema_filtered_sf, color='red')

                    sn.scatterplot(x='x', y='y', data=df_highest_max_sf,
                                   color='green')
                    plt.scatter(inflection_point[0], inflection_point[1],marker='o', color='black')
                    if max(data_forces_and_pos['force_z']) < max(foot_smoothed):
                        plt.vlines(inflection_point[0], ymin=min(data_forces_and_pos['force_z']), ymax=max(foot_smoothed), linewidth=0.8)
                    else:
                        plt.vlines(inflection_point[0], ymin=min(foot_smoothed), ymax=max(data_forces_and_pos['force_z']), linewidth=0.8)

                    # plot the std of the mean z force as shady area:
                    # x = np.arange(min(data_forces_and_pos['force_timestamp']), max(data_forces_and_pos['force_timestamp']), 100000000.0)
                    # plt.fill_between(x, neutral_force_mean-neutral_force_std, neutral_force_mean+neutral_force_std, alpha=0.3)
                    # plot the mean of the z force as horizontal line
                    plt.hlines(neutral_force_mean, xmin=min(data_forces_and_pos['force_timestamp']), xmax=max(data_forces_and_pos['force_timestamp']), linewidth=0.8)


                ax.set_xlabel("rosbag timesteps")
                #ax2.set_xlabel("position timesteps")
                plt.ylabel(f'{run_number}_forces')
                plt.legend(loc='best')
                plt.setp(ax.get_legend().get_texts(), fontsize='8')  # for legend text

                fig1 = plt.gcf()
                fig1.savefig(os.path.join(output_path, f'{run_number}_force_pos_plot.png'), dpi=300)

                plt.show()

                ### assemble the swing phase data for current run
                #swing_data_run = {}
                list_of_rows = []

                #print(data_forces_and_pos)
                for k,v in swing_phases_feet.items():
                    # Foot and the dict of swings
                    print("k: ", k, "v: ", v)
                    for i, swing in enumerate(v):
                        print('swing: ', swing)
                        # get the timestamps for the swing index:
                        swing_timestamp = [x_values[swing[0]], x_values[swing[1]]]
                        print("swing_timestamp: ", swing_timestamp)
                        run = run_number
                        foot = k
                        sensorfoot = sensorfoot_of_run
                        # find the clostest timestamp of the foot swing phase data to the force data:
                        clostest_low = auxiliaryfunctions.find_closest_value(list(data_forces_and_pos['force_timestamp']), swing_timestamp[0])
                        clostest_high = auxiliaryfunctions.find_closest_value(list(data_forces_and_pos['force_timestamp']), swing_timestamp[1])
                        current_row_interval = [data_forces_and_pos[data_forces_and_pos['force_timestamp'] == clostest_low].index[0],
                                                data_forces_and_pos[data_forces_and_pos['force_timestamp'] == clostest_high].index[0]]
                        print("current_row_interval: ", current_row_interval)
                        force_max = max(data_forces_and_pos.loc[current_row_interval[0]:current_row_interval[1], 'force_z'])
                        force_min = min(data_forces_and_pos.loc[current_row_interval[0]:current_row_interval[1], 'force_z'])
                        force_mean = np.mean(data_forces_and_pos.loc[current_row_interval[0]:current_row_interval[1], 'force_z'])
                        neutral_force = neutral_force_mean
                        gait = summary_data[summary_data['run'] == run]['footfallpattern'].values[0]
                        velocity = summary_data[summary_data['run'] == run]['velocity'].values[0]
                        step_frequency = summary_data[summary_data['run'] == run]['step_frequency'].values[0]
                        surface = summary_data[summary_data['run'] == run]['surface'].values[0]
                        direction = summary_data[summary_data['run'] == run]['direction'].values[0]
                        forcesbiased = summary_data[summary_data['run'] == run]['forcesbiased'].values[0]
                        list_of_rows.append([run, foot, sensorfoot, force_max, force_min, force_mean, neutral_force, gait,
                                            velocity, step_frequency, surface, direction, forcesbiased])
                all_swing_data[run_number] = list_of_rows

            print("all swing data: \n", all_swing_data)
            columns = ['run', 'foot', 'sensorfoot', 'force_max', 'force_min', 'force_mean', 'neutral_force', 'gait',
                       'velocity', 'step_frequency', 'surface', 'direction', 'forcesbiased']
            df_all_swing_data = pd.DataFrame(columns=columns)
            # fill dataframe:
            for k, v in all_swing_data.items():
                for list_row in v:
                    df_all_swing_data.loc[len(df_all_swing_data)] = list_row
            print(df_all_swing_data)

            # save the dataframe:
            df_all_swing_data.to_csv(os.path.join(output_path, "magneto_swing_phase_data.csv"), index=True, header=True)

        else:
            print("no assembled_csv folder. Run forceAnalysis.assemble() first.")

    return
