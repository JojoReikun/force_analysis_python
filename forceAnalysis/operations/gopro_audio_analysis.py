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


def read_and_plot(path_gopro_videos, df_data_info_all, l_gopro_files):
    """
    read in the gopro videos one by one and plot the audio.
    :param path_gopro_videos: folder where gopro videos can be found
    :param df_data_info_all: dataframe containing the trial info for all trial dates including which gopro video matches the trial
    :param l_gopro_files: list of all gopro videos in gopro folder for the selected trial date
    :return:
    """
    print("plotting audios...")
    # test if audio files already exist:
    l_gopro_audio_files = glob(os.path.join(path_gopro_videos, f"*.wav"))
    if len(l_gopro_audio_files) > 0:
        for gopro_aud in l_gopro_audio_files:
            # extract just video name:
            audio_name = gopro_aud.rsplit(os.sep)[-1]
            print(f'currently analysing audio {audio_name}...')
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

            # find peaks > 10000 and more than 100000 frames apart. The distance might vary with speed input
            peaks, _ = find_peaks(signal, height=10000, distance=100000)
            print("peaks: ", peaks)
            diff_peaks = np.diff(peaks)
            # get the median (most common) difference in frames between peaks
            median_diff_peaks = np.median(diff_peaks)
            median_diff_peaks_s = round(median_diff_peaks/f_rate, 2)
            print(f"most common distance between peaks: {median_diff_peaks_s} s  |   in frames: {median_diff_peaks} frames")

            # keep peaks with most common

            plt.plot(time[peaks], signal[peaks], "x")

            plt.hlines(10000, time[0], time[-1], linestyles='--', color='k')

            # shows the plot in new window
            plt.show()

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

    return


######################################################################################################
# main function (called by cli):
def plot_gopro_audio(date):
    """
    1st) read in dataCollectionTable_all to match gopro to trial of user input date
    2nd) find the gopro video folder of date and make file list if videos available
    3rd) iterate through files
      3.1) load in respective gopro videos
      3.2) extract sound and plot
    :return:
    """

    # define path to data collection table (hardcoded for this python function for testing purposes):
    path_experiment_folder = r'D:\Jojo\PhD\CSIRO\magneto_climbing_gait\experiments'
    path_data_all_sheet =  os.path.join(path_experiment_folder, "dataCollectionTable_all.xlsx")
    path_trial_folder = os.path.join(path_experiment_folder, date)
    path_gopro_videos = os.path.join(path_trial_folder, "gopro7_videos")

    # see if there is a folder for gopro videos:
    if os.path.isdir(path_gopro_videos):
        l_gopro_files = glob(os.path.join(path_gopro_videos, "*.MP4"))
    else:
        print("No video for gopro files found for this trial date.")
        l_gopro_files = []

    print(f"{len(l_gopro_files)} go pro videos found for {date}: \n{l_gopro_files}")

    # read in all_info data sheet (DataCollectionTable_all):
    df_data_info_all = pd.read_excel(path_data_all_sheet)
    print(f"dataframe of DataCollectionTable_all: \n{df_data_info_all.head()}")

    # call the function to read in the gopro video and plot the audio for investegatory plotting:
    if len(l_gopro_files) > 0:
        read_and_plot(path_gopro_videos, df_data_info_all, l_gopro_files)
    else:
        print(f"no gopro videos = no audio to plot. Check for videos in trial folder for {date}")

    return