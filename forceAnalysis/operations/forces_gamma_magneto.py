# IMPORTS:
from forceAnalysis.utils import auxiliaryfunctions
from glob import glob
import os
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from mpl_interactions import ioff, panhandler, zoom_factory


def plot_forces_gamma(df_force_file, run_number):
    # Enable scroll to zoom with the help of MPL
    # Interactions library function like ioff and zoom_factory.
    with plt.ioff():
        figure, axis = plt.subplots()
    # creating the bar plot
    plt.title(f"gamma forces for run {run_number}")

    nrows = df_force_file.shape[0]
    x = range(0, nrows)
    Fx = df_force_file["Fx"]
    Fy = df_force_file["Fy"]
    Fz = df_force_file["Fz"]

    min_lim = 33250
    max_lim = 33350
    limits = [min_lim, max_lim]
    plt.plot(x[limits[0]:limits[1]], Fx[limits[0]:limits[1]], color='green', alpha = 0.5, label="Fx")
    plt.plot(x[limits[0]:limits[1]], Fy[limits[0]:limits[1]], color='blue', alpha = 0.5, label="Fy")
    plt.plot(x[limits[0]:limits[1]], Fz[limits[0]:limits[1]], color='red', alpha = 0.5, label="Fz")
    #plt.xlim([0, 20000])
    plt.legend()
    disconnect_zoom = zoom_factory(axis)
    # Enable scrolling and panning with the help of MPL Interactions library function like panhandler.
    pan_handler = panhandler(figure)
    plt.show(config={'scrollZoom': True})

    # TODO: use px color by "force" -> reformat/flatten df first -> zoom into spikes

    return


def forces_gamma_read_files(date, force_files_path):
    """
    This function is called first and reads in the .txt files containing the force data.
    The txt files do not have column names, hence these are added: Fx, Fy, Fz, Tx, Ty, Tz.

    :return:
    """
    print(f"reading in force files for {date}...")

    # list all the available force data files in the force_files_path, format: "YYYY-MM-DD_runXXX.txt":
    force_filelist = glob(os.path.join(force_files_path, "*.txt"))
    print(f"force_filelist for {date} contains {len(force_filelist)} files \n")

    # now read in files and add column names to the force file dataframe:
    forces_gamma_columnnames = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]

    #for force_file in force_filelist:

    force_file = force_filelist[9]      # for debugging only use first force file
    # extract the run number and use as keys for dict_forces_gamma:
    filename_orig = force_file.rsplit(os.sep)[-1]
    filename = filename_orig.replace("run", "*")
    filename = filename.replace(".txt", "*")
    re = filename.split("*")
    run_number = re[1]
    print(f"run_number of force_file {filename_orig}:      {run_number}")

    # read in the force_file (tab delimited) and add column names:
    df_force_file = pd.read_csv(force_file, sep="\t", names=forces_gamma_columnnames)
    # print(df_force_file.head())

    plot_forces_gamma(df_force_file, run_number)


    return


def extract_forces_gamma(date):
    """
    1st) force data files for selected date are listed and read in one by one.
    For debugging purposes a random integer file of this list will be plotted using interactive matplotlib.

    :param date: format YYYY-MM-DD of the trial date. Input by user when calling the cli command extract_gamma_forces(date)
    :return:
    """

    forces_gamma_path = r'D:\Jojo\PhD\CSIRO\magneto_climbing_gait\experiments\magnetoAtUSC_gammaForces'
    force_directory_name = date + "_forcesGamma"
    forces_gamma_path_date = os.path.join(forces_gamma_path, force_directory_name)

    # read in force data for selected date:
    forces_gamma_read_files(date, forces_gamma_path_date)

    # First easy plotting to investigate what force data looks like and what we need to get correct force spike.
    # the interactive matplotlib library mpl_interaction or plotly.express for this to be able to zoom

    return