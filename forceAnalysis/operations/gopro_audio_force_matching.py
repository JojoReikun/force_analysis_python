"""
This is a submodule called from gopro_audio_analysis.py to match the detected audio peaks
to the respective force track.
"""

### IMPORTS:
import pandas as pd
import numpy as np
import os
import wave, sys
from scipy import signal, interpolate
import matplotlib.pyplot as plt
import math


def calc_combined_lat_forces(df_forces):
    l_Fxy = []
    l_Fxy_dir = []

    for row in range(df_forces.shape[0]):
        # iterate through force data and calculate Fxy and its direction. Add to dataframe
        Fxy = np.sqrt(df_forces.loc[row, "Fx"] ** 2 + df_forces.loc[row, "Fy"] ** 2)
        Fxy_dir = np.arctan2(df_forces.loc[row, "Fx"], df_forces.loc[row, "Fy"])*(180.0/math.pi)
        l_Fxy.append(Fxy)
        l_Fxy_dir.append(Fxy_dir)
    df_forces.loc[:, ["Fxy"]] = l_Fxy
    df_forces.loc[:, ["Fxy_dir"]] = l_Fxy_dir
    return df_forces


def extract_force_details(vline_list, df_step4, df_forces, date, i, gait):
    """
    This function is called from within the for loop iterating through the individual audio files in match_audio_and_force()
    to extract max, min, and mean from the individual step intervals.
    This data is stored as a new data sheet (csv saved from df_force_detail) containing:
    "audiofile", "forcefile", "gait", "run", "foot_on_fp", "foot", "step", "step_forceframes_start",
    "step_forceframes_end", "Fx_max", "Fy_max", "Fz_max", "Fx_min", "Fy_min", "Fz_min",
    "Fx_mean", "Fy_mean", "Fz_mean", "Fxy_max", "Fxy_min", "Fxy_mean", "Fxy_dir"

    :param: vline_list: contains the audio peaks in force frames which refer to the steps while foot_on_fp
    :param: df_forces: raw force data
    :param: df_step4: equals df_gammaForces, the df which contains details to force and audio data (step4.csv)
    :param: date: date of trial which is selected for analysis by user. Format: >>YYYY-MM-DD<<
    :param: i: current row of df_forces the match_audio_and_force() function is in, use to get correct info from df_forces here
    :return: df_rows_append: df containing the rows of step intervals for current run i to append
    """

    if "Fxy" not in df_forces.columns:
        df_forces = calc_combined_lat_forces(df_forces)
        print(df_forces.head())

    print(f"\n EXTRACTING STEP WISE FORCE DATA for step4.csv row {i}...\n")

    # creates empty DataFrame with the columns to be filled in with step-wise info. Data for each step will be added to this.
    df_rows_append = pd.DataFrame(columns=["audiofile", "forcefile", "gait", "run", "foot_on_fp", "foot", "step", "step_forceframes_start",
    "step_forceframes_end", "Fx_max", "Fy_max", "Fz_max", "Fx_min", "Fy_min", "Fz_min",
    "Fx_mean", "Fy_mean", "Fz_mean", "Fxy_max", "Fxy_min", "Fxy_mean", "Fxy_dir"])

    # need the plot_vlines_at list, the df_forces, date
    # iterate through the audio peaks of the current run: peak j == 0 to j == 1 is foot_on_fp
    vline_list = [int(n) for n in vline_list]
    for j, vline in enumerate(vline_list):
        # skip index 0 peak cause this is start of interval of first step
        if j == 0:
            continue

        # takes interval from previous j to j and extracts data from step interval:
        else:
            print("are all force values for slice nan? : ", np.isnan(list(df_forces["Fx"][vline_list[j-1]:vline_list[j]])).all())
            if not np.isnan(list(df_forces["Fx"][vline_list[j-1]:vline_list[j]])).all():
                print("force data is available for current interval: step {j-1} to step {j}")
                Fx_max = np.nanmax(df_forces["Fx"][vline_list[j-1]:vline_list[j]])
                Fy_max = np.nanmax(df_forces["Fy"][vline_list[j-1]:vline_list[j]])
                Fz_max = np.nanmax(df_forces["Fz"][vline_list[j-1]:vline_list[j]])
                Fx_min = np.nanmin(df_forces["Fx"][vline_list[j-1]:vline_list[j]])
                Fy_min = np.nanmin(df_forces["Fy"][vline_list[j-1]:vline_list[j]])
                Fz_min = np.nanmin(df_forces["Fz"][vline_list[j-1]:vline_list[j]])
                Fx_mean = np.nanmean(df_forces["Fx"][vline_list[j-1]:vline_list[j]])
                Fy_mean = np.nanmean(df_forces["Fy"][vline_list[j-1]:vline_list[j]])
                Fz_mean = np.nanmean(df_forces["Fz"][vline_list[j-1]:vline_list[j]])
                Fxy_max = np.nanmax(df_forces["Fxy"][vline_list[j-1]:vline_list[j]])
                Fxy_min = np.nanmin(df_forces["Fxy"][vline_list[j-1]:vline_list[j]])
                Fxy_mean = np.nanmean(df_forces["Fxy"][vline_list[j-1]:vline_list[j]])
                Fxy_dir = np.nanmean(df_forces["Fxy_dir"][vline_list[j-1]:vline_list[j]])

            else:
                print("force data is nan for: step {j-1} to step {j}")
                Fx_max = np.nan
                Fy_max = np.nan
                Fz_max = np.nan
                Fx_min = np.nan
                Fy_min = np.nan
                Fz_min = np.nan
                Fx_mean = np.nan
                Fy_mean = np.nan
                Fz_mean = np.nan
                Fxy_max = np.nan
                Fxy_min = np.nan
                Fxy_mean = np.nan
                Fxy_dir = np.nan

            print(f"Fx_mean: {Fx_mean}, Fy_mean: {Fy_mean}, Fz_mean: {Fz_mean}, Fxy_mean: {Fxy_mean}, Fxy_dir: {Fxy_dir}")

            if j == 1:
                foot_on_fp = int(df_step4["foot_on_fp"][i])

            step = foot_on_fp + (j-1)

            if foot_on_fp == 4:
                foot = "HR"
            elif foot_on_fp == 5:
                foot = "FR"
            else:
                foot = np.nan

            #create single DataFrame column to return and append & assign values to all other columns for current step interval (j-1):j
            run = df_step4["run"][i]
            df_row_append = pd.DataFrame({
                "audiofile": [df_step4["audiofile"][i]],
                "forcefile": [f"{date}_run{run}.txt"],
                "run": [run],
                "gait": [gait],
                "foot_on_fp": [foot_on_fp],
                "foot": [foot],
                "step": [step],
                "step_forceframes_start": [vline_list[j-1]],
                "step_forceframes_end": [vline_list[j]],
                "Fx_max": [Fx_max],
                "Fy_max": [Fy_max],
                "Fz_max": [Fz_max],
                "Fx_min": [Fx_min],
                "Fy_min": [Fy_min],
                "Fz_min": [Fz_min],
                "Fx_mean": [Fx_mean],
                "Fy_mean": [Fy_mean],
                "Fz_mean": [Fz_mean],
                "Fxy_max": [Fxy_max],
                "Fxy_min": [Fxy_min],
                "Fxy_mean": [Fxy_mean],
                "Fxy_dir": [Fxy_dir]
                })
            print("df_row_append (data of current step): ", df_row_append)

        df_rows_append = df_rows_append.append(df_row_append, ignore_index=True)

    print("df_rows_append (data of all steps for current run): \n", df_rows_append)

    return df_rows_append


def match_audio_and_force(dict_audio_peaks, path_gammaForces_sheet, l_gopro_audio_files, date, gait):
    """
    this function will use the {date}_gammaForces_step3.csv file and the dict containing the audio peaks from the
    gopro_audio_analysis module.
    The "date_time" and "run" columns will be used to read in the force file belonging to the respective run.
    Only runs with "status_refined" green will be used.

    The user is required to manually add a "foot_on_fp" column to the {date}_gammaForces_step3.csv file to extract which
    step is on the force plate given in the comments' column.
    :return:
    """

    ### if interpolation == True, the force data will be upsampled to match the sampling rate of the audio data.
    ### if False, the framerates of each will be converted to times and audio steps converted to force intervals that way.
    interpolation = False
    error_message = "Please manually add a >>foot_on_fp<< column to the {date}_gammaForces_step3.csv file \nto extract which\n\
                    step is on the force plate.\n\
                    Make a copy of this file and name as *_step4.csv\n\
                    Then call the forceAnalysis.plot_gopro_audio() function again."

    print("\n MATCHING AUDIO PEAKS TO FORCE DATA...\n")

    ### force parameter definitions
    sample_rate = 5000          # [Hz]  Seems off by factor of 2!!!!
    default_sample_time = 20   # [s]
    n_samples = 100000
    pretrigger_samples = 90000

    ### Create data frame for step-wise force extraction:
    df_force_detail_colnames = ["audiofile", "forcefile", "gait", "run", "foot_on_fp", "foot", "step", "step_forceframes_start",
                                "step_forceframes_end", "Fx_max", "Fy_max", "Fz_max", "Fx_min", "Fy_min", "Fz_min",
                                "Fx_mean", "Fy_mean", "Fz_mean", "Fxy_max", "Fxy_min", "Fxy_mean", "Fxy_dir"]
    df_force_detail = pd.DataFrame(columns=df_force_detail_colnames)

    ### read in the step4 csv file and respective audio and force data files:
    step4_csv_file = os.path.join(path_gammaForces_sheet, f"{date}_gammaForces_step4.csv")
    try:
        os.path.isfile(step4_csv_file)
    except FileNotFoundError:
        print(error_message)

    df_gammaForces = pd.read_csv(step4_csv_file)

    gammaForces_columns = list(df_gammaForces.columns)

    # check if column "foot_on_fp" exists:
    if "foot_on_fp" in gammaForces_columns:
        ### create directory to save force plots with overlayed audio spikes to:
        if not os.path.exists(os.path.join(path_gammaForces_sheet, "plots")):
            # if the demo_folder directory is not present, create it
            os.makedirs(os.path.join(path_gammaForces_sheet, "plots"))

        # iterate through the runs from this date:
        for row in range(len(df_gammaForces["audiofile"])):
            audio_file_name = df_gammaForces.loc[row, "audiofile"]

            # get the refined status for the run and only proceed if green (all peaks in audio detected)
            refined_satus = df_gammaForces.loc[row, "status_refined"]
            if refined_satus == "green":
                print(f"\n --- matching {audio_file_name} to force data...")

                # find the corresponding filename in list of current audio_file_name
                audio_file_path = [i for i in l_gopro_audio_files if audio_file_name in i][0]
                audio_framerate = df_gammaForces.loc[row, "audio_framerate"]

                ### READ IN THE AUDIO FILE:
                raw = wave.open(audio_file_path)
                # reads all the frames; -1 indicates all or max frames
                signal = raw.readframes(-1)
                signal = np.frombuffer(signal, dtype="int16")
                # cut the audio signal to step peaks interval:
                # get time start and end of step spikes interval
                audio_interval_start_s = df_gammaForces.loc[row, "audio_wave_start_s"]
                audio_interval_end_s = df_gammaForces.loc[row, "audio_wave_end_s"]
                # convert to frames
                f_rate = raw.getframerate()
                f_bytes = raw.getsampwidth()
                print(f"audio details: f_rate = {f_rate}, f_bytes = {f_bytes}")

                # to create a Time Vector spaced linearly with the size of the audio file
                audio_interval_start_frame = int(audio_interval_start_s * f_rate)
                audio_interval_end_frame = int(audio_interval_end_s * f_rate)
                signal_interval = signal[audio_interval_start_frame: audio_interval_end_frame]

                length_audio = len(signal_interval)
                print(f"length of audio data: {length_audio}")

                ### READ IN RESPECTIVE FORCE FILE for current run i (tab delimited) and add column names
                force_file = date + "_run" + str(df_gammaForces.loc[row, "run"]) + ".txt"
                force_file_path = os.path.join(path_gammaForces_sheet, force_file)
                forces_gamma_columnnames = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
                df_force_file = pd.read_csv(force_file_path, sep="\t", names=forces_gamma_columnnames)
                length_force = df_force_file['Fx'].count()
                print(f"length of force data: {length_force}")

                foot_on_fp = int(df_gammaForces.loc[row, "foot_on_fp"])
                print(f"foot on force plate: {foot_on_fp}")
                if foot_on_fp == 4 or foot_on_fp == 8:
                    plot_title = "HR on Force Plate"
                elif foot_on_fp == 5 or foot_on_fp == 9:
                    plot_title = "FR on Force Plate"

                if interpolation == True:
                    ### interpolate force data (5000 Hz) to match the sampling rate of audio data (44100 Hz):
                    # the audio data has a 8.82 times higher sampling rate if force rate 5000 Hz and audio 44100 Hz
                    # new_length_force = int(length_force * 8.82) # force sample rate 5000; seems off in overlayed plot by factor 2
                    new_length_force = int(length_force * 17.64) # audio sample rate 88200 or force data 2500 Hz ?? seems correct
                    print(f"interpolated force data length: {new_length_force}")
                    # create new evenly spaced x-axis for new length of forces
                    xnew = np.linspace(0, new_length_force, num=new_length_force, endpoint=False)

                    # Goal: Increase "samples" for force data to match sample rate of audio data
                    # create interpolation function for the force data
                    for array, array_name in zip([np.array(df_force_file['Fx']), np.array(df_force_file['Fy']), np.array(df_force_file['Fz'])],
                                                 ["Fx", "Fy", "Fz"]):
                        #print(f"\n ----- current force axis: {array_name} -----\n")

                        # compress array
                        array_interp = interpolate.interp1d(np.arange(array.size), array)
                        array_new = array_interp(np.linspace(0, array.size - 1, new_length_force))

                        if array_name == "Fx":
                            ynew_force_x = array_new
                        elif array_name == "Fy":
                            ynew_force_y = array_new
                        elif array_name == "Fz":
                            ynew_force_z = array_new


                    # detect first highest negative peak in interpolated z-forces (should be the step on FP)
                    min_z_force = np.min(ynew_force_z)
                    ind_min_z_force = np.argmin(ynew_force_z)
                    print(f"z_force minimum: {min_z_force}, index: {ind_min_z_force}")

                    ### Plot interpolated forces:
                    print("plotting interpolated forces...")

                    # find the audio peak for the n-th foot, which is the one on fp:
                    # reduce "foot_on_fp" by 1 as foot starts counting at 1 but indices start at 0
                    audio_peak_foot = dict_audio_peaks[audio_file_name][foot_on_fp-1]
                    print(f"audio peak frame of foot on force plate: {audio_peak_foot}")

                    ### now match the audio peak foot spike for "foot_on_fp" onto the min_z_force
                    relevant_audio_peak_frames = dict_audio_peaks[audio_file_name][foot_on_fp-1:(foot_on_fp-1)+5]
                    print("relevant_audio_peak_frames: ", relevant_audio_peak_frames)
                    diff_relevant_audio_peak_frames = np.diff(relevant_audio_peak_frames)
                    diff_relevant_audio_peak_frames = np.insert(diff_relevant_audio_peak_frames, 0, 0)
                    print("diff_relevant_audio_peak_frames: ", diff_relevant_audio_peak_frames)
                    # to each element in the list add the sum of all previous elements, otherwise all hlines will be at a
                    # similar spot as only the relative difference is plotted:
                    absolute_audio_peaks = []
                    for k, item in enumerate(diff_relevant_audio_peak_frames):
                        item_new = sum(diff_relevant_audio_peak_frames[:k+1])
                        # print(item, item_new)
                        absolute_audio_peaks.append(item_new)
                    print("absolute_audio_peaks: ", absolute_audio_peaks)
                    audio_peaks_in_force_frames = [(l+ind_min_z_force) for l in absolute_audio_peaks]
                    print("plot_vlines_at...: ", audio_peaks_in_force_frames)

                    # plot forces:
                    # at min(z_force) plot first hline of audio peak[foot_on_fp - 1]
                    # add other audio peaks as hlines by getting the difference in frames to next peak frame
                    min_lim = 0
                    max_lim = new_length_force
                    limits = [min_lim, max_lim]
                    plt.plot(xnew[limits[0]:limits[1]], ynew_force_x[limits[0]:limits[1]], color='green', alpha=0.5,
                             label="Fx")
                    plt.plot(xnew[limits[0]:limits[1]], ynew_force_y[limits[0]:limits[1]], color='blue', alpha=0.5,
                             label="Fy")
                    plt.plot(xnew[limits[0]:limits[1]], ynew_force_z[limits[0]:limits[1]], color='red', alpha=0.5,
                             label="Fz")

                    plt.scatter(ind_min_z_force, min_z_force)
                    for u, audio_p in enumerate(audio_peaks_in_force_frames):
                        plt.vlines(audio_p, min(ynew_force_z), max(ynew_force_z))
                        plt.text(audio_p + audio_p/100, max(ynew_force_z), f"step {foot_on_fp + u}")
                    plt.title(f"{audio_file_name} - {plot_title} - interp")
                    plt.legend()
                    plt.savefig(os.path.join(path_gammaForces_sheet, "plots",
                                             f"{audio_file_name}_forces_and_audiopeaks.jpg"))  # save as jpg
                    plt.show(block=True)

                    ## call step-wise force extraction function here:
                    df_rows_append = extract_force_details(audio_peaks_in_force_frames, df_gammaForces, df_force_file, date, row, gait)
                    df_force_detail = df_force_detail.append(df_rows_append, ignore_index=True)

                else:
                    # overlay the audio data without upsampling the force data to match audio sampling frequency.
                    # Use framerates and times instead.
                    # audio 44100 frames/s
                    # forces 5000 frames/s

                    # creating new evenly spaced x-axis for new length of forces
                    x = np.linspace(0, length_force, num=length_force, endpoint=False)

                    # detect first highest negative peak in interpolated z-forces (should be the step on FP)
                    min_z_force = np.min(df_force_file['Fz'])
                    ind_min_z_force = np.argmin(df_force_file['Fz'])
                    print(f"z_force minimum: {min_z_force}, index: {ind_min_z_force}")

                    foot_on_fp = int(df_gammaForces.loc[row, "foot_on_fp"])
                    print(f"foot on force plate: {foot_on_fp}")

                    # find the audio peak for the n-th foot, which is the one on fp:
                    # reduce "foot_on_fp" by 1 as foot starts counting at 1 but indices start at 0

                    # if the foot that is on the force plate is the one that fails, there might not be a peak.
                    # foot_on_fp - 1 will throw and index out of bounds error!
                    last_idx = list(dict_audio_peaks[audio_file_name]).index(dict_audio_peaks[audio_file_name][-1])
                    if last_idx < (foot_on_fp - 1):
                        # TODO: for now just set -2 to get it to plot the diagram; filter out in future or do different plot from here
                        audio_peak_foot = dict_audio_peaks[audio_file_name][foot_on_fp - 2] # foot on fp the foot that fails
                    else:
                        audio_peak_foot = dict_audio_peaks[audio_file_name][foot_on_fp - 1]
                        print(f"audio peak frame of foot on force plate: {audio_peak_foot}")

                    ### now match the audio peak foot spike for "foot_on_fp" onto the min_z_force
                    relevant_audio_peak_frames = dict_audio_peaks[audio_file_name][foot_on_fp - 1:(foot_on_fp - 1) + 5]
                    print("relevant_audio_peak_frames: ", relevant_audio_peak_frames)
                    diff_relevant_audio_peak_frames = np.diff(relevant_audio_peak_frames)
                    diff_relevant_audio_peak_frames = np.insert(diff_relevant_audio_peak_frames, 0, 0)

                    # convert frame difference into time interval:
                    diff_relevant_audio_peak_times = [m/f_rate for m in diff_relevant_audio_peak_frames]
                    print("diff_relevant_audio_peak_times: ", diff_relevant_audio_peak_times)

                    ## now convert this to force frame differences:
                    force_sample_rate = 2500
                    diff_audio_in_force_frames = [b*force_sample_rate for b in diff_relevant_audio_peak_times]
                    print("diff_audio_in_force_frames: ", diff_audio_in_force_frames)

                    # to each element in the list add the sum of all previous elements, otherwise all hlines will be at a
                    # similar spot as only the relative difference is plotted:
                    absolute_force_audio_peaks = []
                    for it, item in enumerate(diff_audio_in_force_frames):
                        item_new = sum(diff_audio_in_force_frames[:it + 1])
                        # print(item, item_new)
                        absolute_force_audio_peaks.append(item_new)
                    print("absolute_force_audio_peaks: ", absolute_force_audio_peaks)

                    absolute_force_audio_peaks_plot = [(d + ind_min_z_force) for d in absolute_force_audio_peaks]
                    print("plot_vlines_at...: ", absolute_force_audio_peaks_plot)

                    min_lim = 0
                    max_lim = length_force
                    limits = [min_lim, max_lim]
                    plt.plot(x[limits[0]:limits[1]], df_force_file['Fx'][limits[0]:limits[1]], color='green', alpha=0.5,
                             label="Fx")
                    plt.plot(x[limits[0]:limits[1]], df_force_file['Fy'][limits[0]:limits[1]], color='blue', alpha=0.5,
                             label="Fy")
                    plt.plot(x[limits[0]:limits[1]], df_force_file['Fz'][limits[0]:limits[1]], color='red', alpha=0.5,
                             label="Fz")
                    plt.scatter(ind_min_z_force, min_z_force)
                    plt.legend()
                    for a, audio_p in enumerate(absolute_force_audio_peaks_plot):
                        plt.vlines(audio_p, min(list(df_force_file['Fx'])), max(list(df_force_file['Fx'])))
                        plt.text(audio_p + audio_p/100, max(list(df_force_file['Fx'])), f"step {foot_on_fp + a}")
                    plt.title(f"{audio_file_name} - {plot_title}")
                    plt.savefig(os.path.join(path_gammaForces_sheet, "plots",
                                             f"{audio_file_name}_forces_and_audiopeaks_noInterp.jpg"))  # save as jpg
                    plt.show(block=True)

                    ## call step-wise force extraction function here:
                    df_rows_append = extract_force_details(absolute_force_audio_peaks_plot, df_gammaForces, df_force_file, date, row, gait)
                    df_force_detail = df_force_detail.append(df_rows_append, ignore_index=True)

        #### STORE STEP-WISE FORCE DATA AS CSV FILE:
        force_detail_path = os.path.join(path_gammaForces_sheet, f"{date}_forceDetailsSteps.csv")
        if os.path.exists(force_detail_path):
            print(f"{date}_forceDetailsSteps.csv  already exists. To overwrite delete the current file in folder:\n{force_detail_path}")
        else:
            df_force_detail.to_csv(force_detail_path, index=False)

    else:
        print(error_message)
        exit()

    return