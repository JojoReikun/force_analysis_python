### IMPORTS:
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd
import os.path
from forceAnalysis.utils import auxiliaryfunctions


def reorder_data(data):
    remove = ['max_force_x', 'max_force_y', 'max_force_z']
    add = ['max_force_axis', 'max_force_value']
    columnnames = [col for col in data.columns if col not in remove]
    columnnames = columnnames[1:] + add
    print("columnnames: ", columnnames)
    data_reordered = pd.DataFrame(columns=columnnames, index=range(data.shape[0]*3))
    row = 0
    for i in range(1, ((data.shape[0]*3)+1)):
        print("row :", row)
        if i % 3 == 0:
            row += 1
            print("row upped: ", row)

        # fill in dataframe_reordered



    return data_reordered


def plot_summary(overwrite_plots):
    if overwrite_plots == True:
        path = os.path.join(os.getcwd(), "assembled_csv", "summary_data")
        filepath = os.path.join(path, 'summary_data.csv')
        output_path = os.path.join(path, "summary_plots")
        auxiliaryfunctions.attempttomakefolder(output_path)

        if os.path.isfile(filepath):
            data = pd.read_csv(filepath)
            data_forces = data[['max_force_x', 'max_force_y', 'max_force_z']]
            print("data_forces: \n", data_forces.head())

            # reorder data:
            reorder_data(data)

            run_number = filepath.rsplit(os.sep, 1)[1]
            run_number = run_number.split("_", 1)[0]

            colours = ['#e3433d', '#0b6ade', '#5bdea5']
            sn.set_palette(colours)
            sn.set_style('whitegrid')
            sn.boxplot(data=data_forces)
            sn.swarmplot(data=data_forces, color="grey", alpha=0.5)
            plt.ylabel(f'{run_number}_max_forces')

            fig1 = plt.gcf()
            fig1.savefig(os.path.join(output_path, f'{run_number}_forceplot_plot.png'))

            plt.show()
