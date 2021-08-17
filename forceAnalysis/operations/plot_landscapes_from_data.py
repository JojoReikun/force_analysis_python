import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os


def plot_heatmaps(date):
    # for now hard code the paths which are used in assemble as well# generate folder structure for result files:
    result_path = os.path.join(os.getcwd(), "result_files")
    result_trial_path = os.path.join(result_path, date)

    path_summary = os.path.join(result_trial_path, "summary_data")

    if date == "2021-03-30":
        if os.listdir(path_summary) != []:
            data_summary = pd.read_csv(os.path.join(path_summary, "summary_data.csv"))
            plot_data = data_summary.pivot_table(index="step_frequency", columns="velocity", values="climbed_distance", aggfunc=np.nanmean)
            ax = sns.heatmap(plot_data)
            plt.title(date)

            plt.savefig(os.path.join(path_summary, f"{date}_plot.jpg"))
            print(f"plot successfully saved to: {path_summary}")
            plt.show()

    elif date == "2021-03-31":
        """
        this is the data set combined summary file from 2021-03-31 and 2021-04-01.
        The data from 2021-03-30 was added to get footratio 0.9.
        Trial set examined was gait1, foot ratio over velocity in small increments.
        """
        if os.listdir(path_summary) != []:
            data_summary = pd.read_csv(os.path.join(path_summary, "summary_data.csv"))
            plot_data = data_summary.pivot_table(index="footratio", columns="velocity", values="climbed_distance",
                                                 aggfunc=np.nanmean)
            ax = sns.heatmap(plot_data)
            plt.title(date)

            plt.savefig(os.path.join(path_summary, f"{date}_plot.jpg"))
            print(f"plot successfully saved to: {path_summary}")
            plt.show()

    elif date == "2021-04-07":
        """
        this is the data set combined summary file from 2021-04-07, 2021-04-08, 2021-04-10, and 2021-04-14.
        Trial set examined was gait2, foot ratio over velocity in small increments.
        """
        if os.listdir(path_summary) != []:
            data_summary = pd.read_csv(os.path.join(path_summary, "summary_data.csv"))
            plot_data = data_summary.pivot_table(index="footratio", columns="velocity", values="climbed_distance",
                                                 aggfunc=np.nanmean)
            ax = sns.heatmap(plot_data)
            plt.title(date)

            plt.savefig(os.path.join(path_summary, f"{date}_plot.jpg"))
            print(f"plot successfully saved to: {path_summary}")
            plt.show()

    else:
        print("no plot defined for this date")
        exit()

    return