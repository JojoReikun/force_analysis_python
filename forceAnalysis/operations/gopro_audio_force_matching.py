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

    error_message = "Please manually add a >>foot_on_fp<< column to the {date}_gammaForces_step3.csv file \nto extract which\n\
                    step is on the force plate.\n\
                    Make a copy of this file and name as *_step4.csv\n\
                    Then call the forceAnalysis.plot_gopro_audio() function again."

    ### force parameter definitions
    sample_rate = 5000          # [Hz]
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
                l_audio_peaks = dict_audio_peaks[df_gammaForces.loc[i, "audiofile"]]

                # read in the audio file:
                raw = wave.open(audio_file_path)
                # reads all the frames; -1 indicates all or max frames
                signal = raw.readframes(-1)
                signal = np.frombuffer(signal, dtype="int16")
                length_audio = len(signal)
                print(f"length of audio data: {length_audio}")

                # read in respective force file for current run i (tab delimited) and add column names
                force_file = date + "_run" + str(df_gammaForces.loc[i, "run"]) + ".txt"
                force_file_path = os.path.join(path_gammaForces_sheet, force_file)
                forces_gamma_columnnames = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
                df_force_file = pd.read_csv(force_file_path, sep="\t", names=forces_gamma_columnnames)
                length_force = df_force_file['Fx'].count()
                print(f"length of force data: {length_force}")

                ### interpolate force data (5000 Hz) to match the sampling rate of audio data (44100 Hz):
                # the audio data has a 8.82 times higher sampling rate
                new_length_force = int(length_force * 8.82)
                print(f"interpolated force data length: {new_length_force}")
                # create new evenly spaced x-axis for new length of forces
                xnew = np.linspace(0, new_length_force, num=new_length_force, endpoint=False)

                # TODO: fix interpolation. I had to do this in ClimbingLizardForceAnalysis. Adjust to average frames and up or downsample
                # TODO: see: https://stackoverflow.com/questions/38064697/interpolating-a-numpy-array-to-fit-another-array
                # Goal: Increase "samples" for force data to match sample rate of audio data

                # create interpolation function for the force data
                f_force_x = interpolate.KroghInterpolator(range(length_force), df_force_file['Fx'])
                f_force_y = interpolate.KroghInterpolator(range(length_force), df_force_file['Fy'])
                f_force_z = interpolate.KroghInterpolator(range(length_force), df_force_file['Fz'])
                print(f_force_x)
                # get new force data points:
                ynew_force_x = list(f_force_x(xnew))
                ynew_force_y = list(f_force_y(xnew))
                ynew_force_z = list(f_force_z(xnew))

                # test print:
                print("ynew_force_x: ", ynew_force_x)

                # detect first highest negative peak in interpolated z-forces (should be the step on FP)
                min_z_force = min(ynew_force_z)
                ind_min_z_force = ynew_force_z.index(min_z_force)
                print(f"z_force minimum: {min_z_force}, index: {ind_min_z_force}")

                ### Plot interpolated forces:
                print("plotting interpolated forces...")
                min_lim = 0
                max_lim = len(ynew_force_x)
                limits = [min_lim, max_lim]
                plt.plot(xnew[limits[0]:limits[1]], ynew_force_x[limits[0]:limits[1]], color='green', alpha=0.5, label="Fx")
                plt.plot(xnew[limits[0]:limits[1]], ynew_force_y[limits[0]:limits[1]], color='blue', alpha=0.5, label="Fy")
                plt.plot(xnew[limits[0]:limits[1]], ynew_force_z[limits[0]:limits[1]], color='red', alpha=0.5, label="Fz")
                plt.show()

                foot_on_fp = int(df_gammaForces.loc[i, "foot_on_fp"])
                print(f"foot on force plate: {foot_on_fp}")

                # find the audio peak for the n-th foot, which is the one on fp:
                audio_peak_foot = dict_audio_peaks[audio_file_name][foot_on_fp]

                ### now extract the audio interval and put the spike for "foot_on_fp" onto the min_z_force

    else:
        print(error_message)
        exit()

    return