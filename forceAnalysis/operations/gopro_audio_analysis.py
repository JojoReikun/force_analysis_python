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


def plot_audio(l_gopro_audio_files):
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
        peaks, _ = find_peaks(signal, height=10000, distance=200000)
        print("peaks: ", peaks)
        diff_peaks = np.diff(peaks)
        # get the median (most common) difference in frames between peaks
        median_diff_peaks = np.median(diff_peaks)
        median_diff_peaks_s = round(median_diff_peaks / f_rate, 2)
        print(f"most common distance between peaks: {median_diff_peaks_s} s  |   in frames: {median_diff_peaks} frames")

        plt.plot(time[peaks], signal[peaks], "x")

        plt.hlines(10000, time[0], time[-1], linestyles='--', color='k')

        # shows the plot in new window
        plt.show()
    return


def step3_analyse_and_extract_spikes():
    return


def step2_plot_and_spikes(l_gopro_audio_files, df_gammaForces, bool_plot_audio):
    """
    :param l_gopro_audio_files:
    :param df_gammaForces:
    :param bool_plot_audio: boolean, default False. If true: Plots audio anyway, even if STep2 has been completed and intervals have been extracted already.
    :return:
    """
    gammaForces_columns = list(df_gammaForces.columns)
    #print("columns of the gammaForces csv file: \n", gammaForces_columns)
    columns_needed = ["audio_wave_start_s", "audio_wave_end_s", "comments_audio", "status"]

    # check if columns of audio intervals exist already -> exit and do step3 instead. (analyse and extract peaks)
    if all(item in gammaForces_columns for item in columns_needed):
        if bool_plot_audio == True:
            # plot audio tracks anyway:
            plot_audio(l_gopro_audio_files)
        print(">> audio has been plotted and audio intervals extracted already... continue with Step3\n\n")
        return

    # otherwise load & plot the audio tracks to extract the spikes:
    else:
        print("loading and plotting audio tracks...")
        plot_audio(l_gopro_audio_files)
        print("\nmanually add 4 columns: [audio_wave_start_s, audio_wave_end_s, comment_audio, status]")
        print("look at the plots of the audio tracks & add start and end frame of the step spikes into the csv file.")
        print("add a status to the audio of the trial. Detailed explanation of how this works in README.md")
        print("once completed, rerun forceAnalysis.plot_gopro_audio() in the console.")
    return


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
      3.3)
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

    # read in data sheets:
    # (DataCollectionTable_all):
    df_data_info_all = pd.read_excel(path_data_all_sheet)
    print(f"dataframe of DataCollectionTable_all: \n{df_data_info_all.head()}")
    # {date}_gammaForces.csv:
    df_gammaForces = pd.read_csv(os.path.join(path_gammaForces_sheet, f"{date}_gammaForces.csv"))

    # call the function to read in the gopro video and plot the audio for investigatory plotting:
    # check if there are actually videos in the gopro folder:
    if len(l_gopro_files) > 0:
        # leads over to Step1.
        l_gopro_audio_files = step1_read_and_convert(path_gopro_videos, l_gopro_files)
        # once Step1 is done, lead to Step2:
        step2_plot_and_spikes(l_gopro_audio_files, df_gammaForces, bool_plot_audio)
        # for step3 manual extraction of audio spike intervals and status descriptions are needed in "{date}_gammaForces.csv"
        # step 3:

    # otherwise, warn of absence of gopro videos and quit:
    else:
        print(f"no gopro videos = no audio to plot. Check for videos in trial folder for {date}")
        exit()

    return