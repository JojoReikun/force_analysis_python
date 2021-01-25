# https://pythonforundergradengineers.com/piston-motion-with-python-matplotlib.html

### IMPORTS:
import os
from glob import glob
from forceAnalysis.utils import auxiliaryfunctions
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
import matplotlib.animation as animation

feet = ['FR', 'FL', 'HL', 'HR']
COM = (0,0)


def animate():
    # following plots
    return


def animate_magneto(overwrite_plots):
    if overwrite_plots == True:
        path = os.path.join(os.getcwd(), "assembled_csv")

        output_path = os.path.join(path, "force_and_position_plots")
        auxiliaryfunctions.attempttomakefolder(output_path)

        if os.path.isdir(path):
            for file in glob(os.path.join(path, "*.csv")):
                data = pd.read_csv(file)
                sensorfoot = data['sensorfoot'][1]

                max_data_points = 100000
                for foot in feet:
                    data_points = data[f'{foot}_pos_x'].count()
                    if data_points < max_data_points:
                        max_data_points = data_points

                run_number = file.rsplit(os.sep, 1)[1]
                run_number = run_number.split("_", 1)[0]

                FR_coordinates = []
                FL_coordinates = []
                HL_coordinates = []
                HR_coordinates = []

                for i in range(max_data_points):
                    # potentially add last coordinate on top to see Magneto move
                    FR_coordinates.append((data['FR_pos_x'][i], data['FR_pos_y'][i]))
                    FL_coordinates.append((data['FL_pos_x'][i], data['FL_pos_y'][i]))
                    HL_coordinates.append((data['HL_pos_x'][i], data['HL_pos_y'][i]))
                    HR_coordinates.append((data['HR_pos_x'][i], data['HR_pos_y'][i]))

                colours = ['#e3433d', '#0b6ade', '#5bdea5', '#690612', '#150669', '#1c5239']
                sn.set_style('whitegrid')

                for n in range(len(FR_coordinates)):
                    # set up plot figure:
                    fig = plt.figure()
                    ax = fig.add_subplot(aspect="equal", autoscale_on=False)


    return
