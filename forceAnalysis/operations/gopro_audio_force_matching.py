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


def match_audio_and_force(dict_audio_peaks, path_gammaForces_sheet, l_gopro_audio_files, date):
    """
    this function will use the {date}_gammaForces_step3.csv file and the dict containing the audio peaks from the
    gopro_audio_analysis module.
    The "date_time" and "run" columns will be used to read in the force file belonging to the respective run.
    Only runs with "status_refined" green will be used.

    The user is required to manually add a "foot_on_fp" column to the {date}_gammaForces_step3.csv file to extract which
    step is on the force plate given in the comments' column.
    :return:
    """

    interpolation = True
    error_message = "Please manually add a >>foot_on_fp<< column to the {date}_gammaForces_step3.csv file \nto extract which\n\
                    step is on the force plate.\n\
                    Make a copy of this file and name as *_step4.csv\n\
                    Then call the forceAnalysis.plot_gopro_audio() function again."

    ### force parameter definitions
    sample_rate = 5000          # [Hz]  Seems off by factor of 2!!!!
    default_sample_time = 20   # [s]
    n_samples = 100000
    pretrigger_samples = 90000

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
        # iterate through the runs from this date:
        for i in range(len(df_gammaForces["audiofile"])):
            audio_file_name = df_gammaForces.loc[i, "audiofile"]

            # get the refined status for the run and only proceed if green (all peaks in audio detected)
            refined_satus = df_gammaForces.loc[i, "status_refined"]
            if refined_satus == "green":
                print(f"\n --- matching {audio_file_name} to force data...")

                # find the corresponding filename in list of current audio_file_name
                audio_file_path = [i for i in l_gopro_audio_files if audio_file_name in i][0]
                audio_framerate = df_gammaForces.loc[i, "audio_framerate"]

                ### READ IN THE AUDIO FILE:
                raw = wave.open(audio_file_path)
                # reads all the frames; -1 indicates all or max frames
                signal = raw.readframes(-1)
                signal = np.frombuffer(signal, dtype="int16")
                # cut the audio signal to step peaks interval:
                # get time start and end of step spikes interval
                audio_interval_start_s = df_gammaForces.loc[i, "audio_wave_start_s"]
                audio_interval_end_s = df_gammaForces.loc[i, "audio_wave_end_s"]
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
                force_file = date + "_run" + str(df_gammaForces.loc[i, "run"]) + ".txt"
                force_file_path = os.path.join(path_gammaForces_sheet, force_file)
                forces_gamma_columnnames = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
                df_force_file = pd.read_csv(force_file_path, sep="\t", names=forces_gamma_columnnames)
                length_force = df_force_file['Fx'].count()
                print(f"length of force data: {length_force}")

                foot_on_fp = int(df_gammaForces.loc[i, "foot_on_fp"])
                print(f"foot on force plate: {foot_on_fp}")
                if foot_on_fp == 4:
                    plot_title = "FR on Force Plate"
                elif foot_on_fp == 5:
                    plot_title = "HR on Force Plate"

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
                    print("relevant_audio_peak_frames: ", relevant_audio_peak_frames.astype(int))
                    diff_relevant_audio_peak_frames = np.diff(relevant_audio_peak_frames)
                    diff_relevant_audio_peak_frames = np.insert(diff_relevant_audio_peak_frames, 0, 0)
                    print("diff_relevant_audio_peak_frames: ", diff_relevant_audio_peak_frames.astype(int))
                    # to each element in the list add the sum of all previous elements, otherwise all hlines will be at a
                    # similar spot as only the relative difference is plotted:
                    absolute_audio_peaks = []
                    for i, item in enumerate(diff_relevant_audio_peak_frames):
                        item_new = sum(diff_relevant_audio_peak_frames[:i+1])
                        # print(item, item_new)
                        absolute_audio_peaks.append(item_new)
                    print("absolute_audio_peaks: ", absolute_audio_peaks)
                    audio_peaks_in_force_frames = [(i+ind_min_z_force) for i in absolute_audio_peaks]
                    print("plot_vlines_at...: ", audio_peaks_in_force_frames)
                    # TODO: it looks like later added peaks are not included in audio_peak_dict?

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
                    for i, audio_p in enumerate(audio_peaks_in_force_frames):
                        plt.vlines(audio_p, min(ynew_force_z), max(ynew_force_z))
                        plt.text(audio_p + audio_p/100, max(ynew_force_z), f"step {foot_on_fp + i}")
                    plt.title(f"{audio_file_name} - {plot_title} - interp")
                    plt.savefig(os.path.join(path_gammaForces_sheet, "plots",
                                             f"{audio_file_name}_forces_and_audiopeaks.jpg"))  # save as jpg
                    plt.show(block=True)

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

                    foot_on_fp = int(df_gammaForces.loc[i, "foot_on_fp"])
                    print(f"foot on force plate: {foot_on_fp}")

                    # find the audio peak for the n-th foot, which is the one on fp:
                    # reduce "foot_on_fp" by 1 as foot starts counting at 1 but indices start at 0
                    audio_peak_foot = dict_audio_peaks[audio_file_name][foot_on_fp - 1]
                    print(f"audio peak frame of foot on force plate: {audio_peak_foot}")

                    ### now match the audio peak foot spike for "foot_on_fp" onto the min_z_force
                    relevant_audio_peak_frames = dict_audio_peaks[audio_file_name][foot_on_fp - 1:(foot_on_fp - 1) + 5]
                    print("relevant_audio_peak_frames: ", relevant_audio_peak_frames)
                    diff_relevant_audio_peak_frames = np.diff(relevant_audio_peak_frames)
                    diff_relevant_audio_peak_frames = np.insert(diff_relevant_audio_peak_frames, 0, 0)

                    # convert frame difference into time interval:
                    diff_relevant_audio_peak_times = [i/f_rate for i in diff_relevant_audio_peak_frames]
                    print("diff_relevant_audio_peak_times: ", diff_relevant_audio_peak_times)

                    ## now convert this to force frame differences:
                    force_sample_rate = 2500
                    diff_audio_in_force_frames = [i*force_sample_rate for i in diff_relevant_audio_peak_times]
                    print("diff_audio_in_force_frames: ", diff_audio_in_force_frames)

                    # to each element in the list add the sum of all previous elements, otherwise all hlines will be at a
                    # similar spot as only the relative difference is plotted:
                    absolute_force_audio_peaks = []
                    for i, item in enumerate(diff_audio_in_force_frames):
                        item_new = sum(diff_audio_in_force_frames[:i + 1])
                        # print(item, item_new)
                        absolute_force_audio_peaks.append(item_new)
                    print("absolute_force_audio_peaks: ", absolute_force_audio_peaks)

                    absolute_force_audio_peaks_plot = [(i + ind_min_z_force) for i in absolute_force_audio_peaks]
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
                    for i, audio_p in enumerate(absolute_force_audio_peaks_plot):
                        plt.vlines(audio_p, min(list(df_force_file['Fx'])), max(list(df_force_file['Fx'])))
                        plt.text(audio_p + audio_p/100, max(list(df_force_file['Fx'])), f"step {foot_on_fp + i}")
                    plt.title(f"{audio_file_name} - {plot_title}")
                    plt.savefig(os.path.join(path_gammaForces_sheet, "plots",
                                             f"{audio_file_name}_forces_and_audiopeaks_noInterp.jpg"))  # save as jpg
                    plt.show(block=True)

    else:
        print(error_message)
        exit()

    return