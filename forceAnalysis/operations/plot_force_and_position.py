def plot_force_data_and_position_data(overwrite_plots):
    import matplotlib.pyplot as plt
    import seaborn as sn
    import pandas as pd
    import os.path
    import numpy as np
    from glob import glob
    from forceAnalysis.utils import auxiliaryfunctions

    feet = ['FR', 'FL', 'HR', 'HL']

    if overwrite_plots == True:
        path = os.path.join(os.getcwd(), "assembled_csv")

        output_path = os.path.join(path, "force_and_position_plots")
        auxiliaryfunctions.attempttomakefolder(output_path)

        if os.path.isdir(path):
            for file in glob(os.path.join(path, "*.csv")):
                data = pd.read_csv(file)
                sensorfoot = data['sensorfoot'][1]
                data_forces_and_pos = data[['force_x', 'force_y', 'force_z', 'FR_pos_x', 'FL_pos_x', 'HR_pos_x', 'HL_pos_x']]
                print("data_forces_and_pos: ", data_forces_and_pos.head())

                x_forces = range(data_forces_and_pos['force_x'].count())

                min_x_pos = range(100000)
                for foot in feet:
                    x_pos = range(data_forces_and_pos[f'{foot}_pos_x'].count())
                    if len(x_pos) < len(min_x_pos):
                        min_x_pos = x_pos

                run_number = file.rsplit(os.sep, 1)[1]
                run_number = run_number.split("_", 1)[0]

                colours = ['#e3433d', '#0b6ade', '#5bdea5', '#690612', '#150669', '#1c5239']
                sn.set_style('whitegrid')

                scalefactor = 500
                FR_pos_x = data_forces_and_pos[f'FR_pos_x'].dropna()
                FR_pos_x = [y * scalefactor for y in FR_pos_x]
                FR_pos_x = FR_pos_x[0:len(min_x_pos)]
                FL_pos_x = data_forces_and_pos[f'FL_pos_x'].dropna()
                FL_pos_x = [y * scalefactor for y in FL_pos_x]
                FL_pos_x = FL_pos_x[0:len(min_x_pos)]
                HR_pos_x = data_forces_and_pos[f'HR_pos_x'].dropna()
                HR_pos_x = [y * -1*scalefactor for y in HR_pos_x]
                HR_pos_x = HR_pos_x[0:len(min_x_pos)]
                HL_pos_x = data_forces_and_pos[f'HL_pos_x'].dropna()
                HL_pos_x = [y * -1*scalefactor for y in HL_pos_x]
                HL_pos_x = HL_pos_x[0:len(min_x_pos)]

                fig, ax = plt.subplots()
                ax2 = ax.twiny()
                sn.lineplot(x = x_forces, y = data_forces_and_pos['force_x'], data=data_forces_and_pos, ax=ax, color=colours[0], label=f'{sensorfoot}_force_x')
                sn.lineplot(x = x_forces, y = data_forces_and_pos['force_y'], data=data_forces_and_pos, ax=ax, color=colours[1], label=f'{sensorfoot}_force_y')
                sn.lineplot(x = x_forces, y = data_forces_and_pos['force_z'], data=data_forces_and_pos, ax=ax, color=colours[2], label=f'{sensorfoot}_force_z')

                sn.lineplot(x = min_x_pos, y = FR_pos_x, data=data_forces_and_pos, ax=ax2, palette=[colours[3]], label='FR', dashes=[(2,2)], linewidth=1)
                sn.lineplot(x = min_x_pos, y = FL_pos_x, data=data_forces_and_pos, ax=ax2, palette=[colours[3]], label='FL', dashes=[(2,2)], linewidth=1)
                sn.lineplot(x = min_x_pos, y = HR_pos_x, data=data_forces_and_pos, ax=ax2, palette=[colours[3]], label='HR', dashes=[(2,2)], linewidth=1)
                sn.lineplot(x = min_x_pos, y = HL_pos_x, data=data_forces_and_pos, ax=ax2, palette=[colours[3]], label='HL', dashes=[(2,2)], linewidth=1)

                ax.set_xlabel("force timesteps")
                ax2.set_xlabel("position timesteps")
                plt.ylabel(f'{run_number}_forces')

                fig1 = plt.gcf()
                fig1.savefig(os.path.join(output_path, f'{run_number}_force_pos_plot.png'))

                plt.show()

    return