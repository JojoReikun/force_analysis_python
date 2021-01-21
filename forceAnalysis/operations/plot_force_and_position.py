def smooth_foot_position(foot_pos_x, foot_timestamp, sample_spacing_foot, df_current_run_summary, filtertype):
    """
    takes the values for the x-position data of the sensorfoot and smoothes them using Savitzky-Golay filter
    or the butterworth low-pass filter
    filter: "savgol" or "butter"
    """
    #IMPORTS:
    from scipy import signal
    from scipy import fft, ifft
    import matplotlib.pyplot as plt
    import numpy as np

    print("smoothing...")

    x_values = list(foot_timestamp)
    if filtertype == "savgol":
        y_values_savgol = signal.savgol_filter(foot_pos_x, 17, 3)  # iterable, windowlength
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
        auxiliaryfunctions.attempttomakefolder(output_path)

        if os.path.isdir(summary_path):
            summary_data = pd.read_csv(os.path.join(summary_path, "summary_data.csv"))
            data_vel_and_freq = summary_data[['run', 'velocity', 'step_frequency']]
        if os.path.isdir(path):
            number_of_files = len(glob(os.path.join(path, "*.csv")))
            for i, file in enumerate(glob(os.path.join(path, "*.csv"))):
                print("Progress: ", i, "/", number_of_files)

                data = pd.read_csv(file)
                sensorfoot = data['sensorfoot'][1]
                data_forces_and_pos = data[['force_x', 'force_y', 'force_z', 'FR_pos_x', 'FL_pos_x', 'HR_pos_x', 'HL_pos_x',
                                            'force_timestamp', 'imu_linacc_y', 'imu_timestamp', 'FR_timestamp', 'FL_timestamp',
                                            'HR_timestamp', 'HL_timestamp']]

                #print("data_forces_and_pos: ", data_forces_and_pos.head())

                sample_spacing_foot = data_forces_and_pos['FR_timestamp'][5] - data_forces_and_pos['FR_timestamp'][4]
                sample_spacing_force = data_forces_and_pos['force_timestamp'][5] - data_forces_and_pos['force_timestamp'][4]
                #print("sample freq foot: ", sample_spacing_foot,
                #      "\nsample freq force: ", sample_spacing_force)

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
                print(df_current_run_summary)

                print("run number: ", run_number, "min_x_pos: ", len(min_x_pos))

                colours = ['#e3433d', '#0b6ade', '#5bdea5', '#690612', '#150669', '#1c5239']
                sn.set_style('whitegrid')

                scalefactor = 500
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
                if smoothing == True:
                    # get sensorfoot:
                    sensorfoot_of_run = auxiliaryfunctions.get_sensorfoot_for_run(run_number)
                    print(run_number, sensorfoot_of_run)

                    # so far only sensorfoot FR and HR exist:
                    # choose filtertype "savgol", "fft" or "butter"
                    # filtertype = "fft"
                    if isinstance(sensorfoot_of_run, str) and sensorfoot_of_run == "FR":
                        x_values, foot_smoothed = smooth_foot_position(FR_pos_x, data_forces_and_pos['FR_timestamp'][:len(min_x_pos)], sample_spacing_foot, df_current_run_summary, filtertype=filtertype)
                    elif isinstance(sensorfoot_of_run, str) and sensorfoot_of_run == "HR":
                        x_values, foot_smoothed = smooth_foot_position(HR_pos_x, data_forces_and_pos['HR_timestamp'][:len(min_x_pos)], sample_spacing_foot, df_current_run_summary, filtertype=filtertype)

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
                    sn.lineplot(x = x_values, y = foot_smoothed, label=f'{sensorfoot_of_run} pos {filtertype}', linewidth=1)

                ax.set_xlabel("rosbag timesteps")
                #ax2.set_xlabel("position timesteps")
                plt.ylabel(f'{run_number}_forces')

                fig1 = plt.gcf()
                fig1.savefig(os.path.join(output_path, f'{run_number}_force_pos_plot.png'), dpi=300)

                plt.show()

    return