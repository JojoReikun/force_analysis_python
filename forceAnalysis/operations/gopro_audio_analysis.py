"""
The idea is to plot the audio from the gopro videos to try and get the timing of the steps for the gamma force data.
High spikes should be the steps as Magneto's feet CLONK onto the metal.
First see if that assumption is correct, then detect the step spikes and match them to the gamma force data
(knowing how many steps) which foot was on the force plate for.

"""

### IMPORTS
import os
from pathlib import Path
import pandas as pd
from glob import glob
import moviepy.editor as mp
import numpy as np
import wave, sys
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from forceAnalysis.utils import auxiliaryfunctions
from forceAnalysis.operations import gopro_audio_force_matching


def step3_analyse_and_extract_spikes(df_gammaForces, l_gopro_audio_files, date, dict_time_intervals, cutoff_value):
    print("\n\n>>>> Step3: analyse spikes and match to force data")
    # add new columns to df_gammaForces to write refined peaks etc. to it:
    # add an empty columns
    df_gammaForces['interval_peaks'] = ''
    df_gammaForces['nb_detected_peaks'] = ''
    df_gammaForces['med_time_interval'] = ''
    df_gammaForces['med_frame_interval'] = ''
    df_gammaForces['audio_framerate'] = ''
    df_gammaForces['status_refined'] = 'pls update'
    dict_audio_peaks = {}

    # for row in df
        # read in audiofile[row]
        # get status code
        # if red:
            # proceed to next file
        # if orange:
            # set start and end interval frame (in s --> convert to frames)
            # redo find peaks with lower height parameter
            # replot only interval
        # if green:
            # proceed with match_to_gamma_forces()
        # match_to_gamma_forces
        # get average time interval between spikes for current file

    for i in range(len(df_gammaForces["audiofile"])):
        audio_file_name = df_gammaForces.loc[i, "audiofile"]
        print(f"\n --- analysing {audio_file_name}...")
        status = df_gammaForces.loc[i, "status"]

        # find the corresponding filename in list of current audio_file_name
        audio_file_path = [i for i in l_gopro_audio_files if audio_file_name in i][0]

        # read in audio:
        raw = wave.open(audio_file_path)
        # reads all the frames; -1 indicates all or max frames
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype="int16")

        # get time start and end of step spikes interval
        audio_interval_start_s = df_gammaForces.loc[i, "audio_wave_start_s"]
        audio_interval_end_s = df_gammaForces.loc[i, "audio_wave_end_s"]

        # convert to frames
        # gets the frame rate
        f_rate = raw.getframerate()
        # to create a Time Vector spaced linearly with the size of the audio file
        audio_interval_start_frame = int(audio_interval_start_s * f_rate)
        audio_interval_end_frame = int(audio_interval_end_s * f_rate)

        # print(f"audio file: {audio_file_name}, start frame: {audio_interval_start_frame}, end frame: {audio_interval_end_frame}")

        signal_interval = signal[audio_interval_start_frame: audio_interval_end_frame]

        ################################################################################
        # Individual status handling:
        if status == "red":
            print("STATUS RED")
            df_gammaForces.loc[i, "status_refined"] = df_gammaForces.loc[i, "status"]
            continue

        if status == "green":
            print("STATUS GREEN")
            df_gammaForces.loc[i, "status_refined"] = df_gammaForces.loc[i, "status"]

            # detect the spikes with original cut-off frequency (cutoff_value)
            peaks, _ = find_peaks(signal_interval, height=cutoff_value, distance=200000)

            # write peaks to dict_audio_peaks
            dict_audio_peaks[audio_file_name] = peaks
            continue

        if status == "orange":
            print("STATUS ORANGE")
            # to Plot the x-axis in seconds get the frame rate and divide by size of your signal
            # to create a Time Vector spaced linearly with the size of the audio file
            x = np.linspace(audio_interval_start_frame, audio_interval_end_frame, len(signal_interval)) # start, stop, num

            # plot:
            # plot audio:
            plt.figure(1)
            # title of the plot
            plt.title(f"Sound Wave Interval of {audio_file_name}")
            # label of x-axis
            plt.xlabel("Frames")
            # actual plotting
            plt.plot(x, signal_interval, alpha=0.7, color = "gray")

            # detect spikes with original cut-off frequency (cutoff_value)
            peaks, _ = find_peaks(signal_interval, height=cutoff_value, distance=200000)
            plt.plot(x[peaks], signal_interval[peaks], "x", color = "g")
            plt.hlines(cutoff_value, x[0], x[-1], linestyles='--', color='g')

            new_cutoff = 7000
            new_peaks, _ = find_peaks(signal_interval, height=new_cutoff, distance=200000)
            # make list with peaks which are not in previous peaks
            only_new_peaks = [i for i in new_peaks if i not in peaks]

            # plot only new found peaks in red
            plt.plot(x[only_new_peaks], signal_interval[only_new_peaks], "o", color="r")
            plt.hlines(new_cutoff, x[0], x[-1], linestyles='--', color='r')

            # shows the plot in new window
            plt.show()

            #################################################################
            # write peaks as list and average time interval into df
            all_peaks = np.concatenate((peaks, only_new_peaks), axis=None)
            all_peaks = sorted(all_peaks)   # sort peaks so they appear in order in list.
            print("all_peaks: ", all_peaks)
            #all_peaks = all_peaks.astype("int32")

            # write peaks to dict_audio_peaks
            dict_audio_peaks[audio_file_name] = all_peaks

            # write all_peaks, and average_time interval from dict to df
            # df_gammaForces.loc[i, "interval_peaks"] = all_peaks   # doesn't work like this to write array into df cell...
            df_gammaForces.loc[i, "med_time_interval"] = dict_time_intervals[audio_file_name][1]
            df_gammaForces.loc[i, "med_frame_interval"] = dict_time_intervals[audio_file_name][0]
            df_gammaForces.loc[i, "audio_framerate"] = f_rate
            df_gammaForces.loc[i, "nb_detected_peaks"] = len(all_peaks)


    print(df_gammaForces.head(10))
    print("DONE\n\n")

    return df_gammaForces, dict_audio_peaks


def step2_plot_and_spikes(l_gopro_audio_files):
    """
    :param l_gopro_audio_files: file list of GoPro audio files
    :return: dict_time_intervals: contains the audio filename as keys and a list with median time interval between
                                spikes in frames and seconds
    """
    # load & plot the audio tracks to extract the spikes:

    print("loading and plotting audio tracks...")

    dict_time_intervals = {}

    for gopro_aud in l_gopro_audio_files:
        # extract just video name:
        audio_name = gopro_aud.rsplit(os.sep)[-1]
        print(f'\n >>> currently analysing audio {audio_name}...')
        raw = wave.open(gopro_aud)
        # reads all the frames
        # -1 indicates all or max frames
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype="int16")

        # looking at the raw plots spikes for footsteps seem to be >10000, find all spikes there:
        print(f"signal: {signal}")

        # gets the frame rate
        f_rate = raw.getframerate()

        # to Plot the x-axis in seconds get the frame rate and divide by size of your signal
        # to create a Time Vector spaced linearly with the size of the audio file
        time = np.linspace(0, len(signal) / f_rate, num=len(signal))

        # plot audio:
        plt.figure(1)
        # title of the plot
        plt.title(f"Sound Wave of {audio_name}")
        # label of x-axis
        plt.xlabel("Time")
        # actual plotting
        plt.plot(time, signal, alpha=0.7)

        # find peaks > 10000 and more than 200000 frames apart. Note: The distance might vary with speed input!
        cutoff_value = 10000
        peaks, _ = find_peaks(signal, height=cutoff_value, distance=200000)
        print("peaks: ", peaks)
        diff_peaks = np.diff(peaks)
        # get the median (most common) difference in frames between peaks
        median_diff_peaks = np.median(diff_peaks)
        median_diff_peaks_s = round(median_diff_peaks / f_rate, 2)
        print(f"most common distance between peaks: {median_diff_peaks_s} s  |   in frames: {median_diff_peaks} frames")
        dict_time_intervals[audio_name] = [median_diff_peaks, median_diff_peaks_s]

        plt.plot(time[peaks], signal[peaks], "x")

        plt.hlines(10000, time[0], time[-1], linestyles='--', color='k')

        # shows the plot in new window
        plt.show()

    return dict_time_intervals, cutoff_value


def step1_read_and_convert(path_gopro_videos, l_gopro_files):
    """
    Test if audio files are already extracted, otherwise convert video to audio files.
    :param path_gopro_videos: folder where gopro videos can be found
    :param l_gopro_files: list of all gopro videos in gopro folder for the selected trial date
    :return: l_gopro_audio_files
    """
    print("GoPro audio  - STEP1: extracting audio files...")

    l_gopro_audio_files = glob(os.path.join(path_gopro_videos, f"*.wav"))
    # audio files exist already -> exit and do step2 instead plot and find peaks
    if len(l_gopro_audio_files) > 0:
        print(">> gopro audio was already extracted. Continue with Step2...\n\n")

    # STEP 1: audio files do not exist yet, perform Step 1 and extract from videos:
    else:
        print("extracting audio files from videos and saving as .wav ...")
        for gopro_vid in l_gopro_files:
            # extract just video name:
            video_name = gopro_vid.rsplit(os.sep)[-1]
            video_name = video_name.split(".")[0]
            print(f'currently analysing video {video_name}...')
            # read in the video and extract audio as wav:
            vid = mp.VideoFileClip(gopro_vid)
            vid.audio.write_audiofile(os.path.join(path_gopro_videos, f"{video_name}.wav"))
            print(f'audio file written as {video_name}.wav')
        l_gopro_audio_files = glob(os.path.join(path_gopro_videos, f"*.wav"))

    return l_gopro_audio_files


#######################################################################################################################
# main function (called by cli):
def plot_gopro_audio(date, bool_plot_audio):
    """
    1st) read in dataCollectionTable_all to match gopro to trial of user input date
    2nd) find the gopro video folder of date and make file list if videos available
    3rd) iterate through files
      3.1) load in respective gopro videos and extract audio
      3.2) plot sound and find spikes (steps)
      Manually find "spikes interval" matching the steps of trial using plots. Detailed description in README.md
      3.3) Using the status code, the interval will then be analysed further. Complete peaks will be written to a
      dict to then match those to the force data of the respective run (status green and orange only)
    :param bool_plot_audio: boolean, default False. If true: Plots audio anyway, even if Step2 has been completed and intervals have been extracted already.
    :return:
    """
    if bool_plot_audio is None:
        bool_plot_audio = False

    # define path to data collection table (hardcoded for this python function for testing purposes):
    path_experiment_folder = r'D:\Jojo\PhD\CSIRO\magneto_climbing_gait\experiments'
    path_data_all_sheet = os.path.join(path_experiment_folder, "dataCollectionTable_all.xlsx")
    path_trial_folder = os.path.join(path_experiment_folder, date)
    path_gopro_videos = os.path.join(path_trial_folder, "gopro7_videos")
    path_gammaForces_sheet = os.path.join(path_experiment_folder, "magnetoAtUSC_gammaForces", f"{date}_forcesGamma")

    # see if there is a folder for gopro videos:
    if os.path.isdir(path_gopro_videos):
        l_gopro_files = glob(os.path.join(path_gopro_videos, "*.MP4"))
    else:
        print("No video for gopro files found for this trial date.")
        l_gopro_files = []

    print(f"{len(l_gopro_files)} go pro videos found for {date}: \n{l_gopro_files}")

    ########################################################
    # READ IN DATA:
    # (DataCollectionTable_all):
    df_data_info_all = pd.read_excel(path_data_all_sheet)
    print(f"dataframe of DataCollectionTable_all: \n{df_data_info_all.head()}")
    # {date}_gammaForces.csv:
    df_gammaForces = pd.read_csv(os.path.join(path_gammaForces_sheet, f"{date}_gammaForces.csv"))
    gammaForces_columns = list(df_gammaForces.columns)
    # print("columns of the gammaForces csv file: \n", gammaForces_columns)
    columns_needed = ["audio_wave_start_s", "audio_wave_end_s", "comments_audio", "status"]

    ########################################################
    # PERFORM AUDIO DATA STEPS:
    # call the function to read in the gopro video and plot the audio for investigatory plotting:
    # check if there are actually videos in the gopro folder:
    if len(l_gopro_files) > 0:
        # >>>> leads over to Step1.
        l_gopro_audio_files = step1_read_and_convert(path_gopro_videos, l_gopro_files)

        # >>>> leads over to Step2.
        dict_time_intervals, cutoff_value = step2_plot_and_spikes(l_gopro_audio_files)

        # for step3 manual extraction of audio spike intervals and status descriptions are needed in "{date}_gammaForces.csv"
        # check if columns of audio intervals exist already -> exit and do step3 instead. (analyse and extract peaks)
        if all(item in gammaForces_columns for item in columns_needed):
            # >>>> leads over to Step3.
            df_gammaForces_updated, dict_audio_peaks = step3_analyse_and_extract_spikes(df_gammaForces, l_gopro_audio_files, date, dict_time_intervals, cutoff_value)
            if os.path.isfile(os.path.join(path_gammaForces_sheet, f"{date}_gammaForces_step3.csv")):
                print("step3 csv already exists.")
            else:
                df_gammaForces_updated.to_csv(os.path.join(path_gammaForces_sheet, f"{date}_gammaForces_step3.csv"))
                print("reanalysed status orange audio files. Please check the new plots and update >>status_refined<< column"
                      " in {date}_gammaForces_step3.csv in \n", path_gammaForces_sheet)

        else:
            print("Still missing needed columns. Fill in manually before executing again.")
            print("\nmanually add 4 columns: [audio_wave_start_s, audio_wave_end_s, comment_audio, status]")
            print("look at the plots of the audio tracks & add start and end frame of the step spikes into the csv file.")
            print("add a status to the audio of the trial. Detailed explanation of how this works in README.md")
            print("once completed, rerun forceAnalysis.plot_gopro_audio() in the console.")

        """
        Now the audio peaks will be matched to the force data to determine where in the force data the steps occur. 
        A submodule is called to do that using the csv file coming out of step3 and the dict_audio_peaks.
        dict_audio_peaks: contains audio_file_name and detected step peaks
        path_gammaForces_sheet: file path to the force folder of selected date
        l_gopro_audio_files: list with all gopro audio file paths
        """
        gopro_audio_force_matching.match_audio_and_force(dict_audio_peaks, path_gammaForces_sheet, l_gopro_audio_files, date)

    # otherwise, warn of absence of gopro videos and quit:
    else:
        print(f"no gopro videos = no audio to plot. Check for videos in trial folder for {date}")
        exit()

    return