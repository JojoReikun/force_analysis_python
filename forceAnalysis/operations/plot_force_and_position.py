def plot_force_data_and_position_data(overwrite_plots):
    import matplotlib.pyplot as plt
    import seaborn as sn
    import pandas as pd
    import os.path
    import numpy as np
    from glob import glob
    from forceAnalysis.utils import auxiliaryfunctions


    if overwrite_plots == True:
        path = os.path.join(os.getcwd(), "assembled_csv")

        output_path = os.path.join(path, "force_and_position_plots")
        auxiliaryfunctions.attempttomakefolder(output_path)

        if os.path.isdir(path):
            for file in glob(os.path.join(path, "*.csv")):
                data = pd.read_csv(file)
                sensorfoot = data['sensorfoot'][1]
                data_forces_and_pos = data[['force_x', 'force_y', 'force_z', f'{sensorfoot}_pos_x', f'{sensorfoot}_pos_y', f'{sensorfoot}_pos_z']]
                print("data_forces_and_pos: ", data_forces_and_pos.head())

                x_forces = range(data_forces_and_pos['force_x'].count())
                x_pos = range(data_forces_and_pos[f'{sensorfoot}_pos_x'].count())

                run_number = file.rsplit(os.sep, 1)[1]
                run_number = run_number.split("_", 1)[0]

                colours = ['#e3433d', '#0b6ade', '#5bdea5']
                sn.set_palette(colours)
                sn.set_style('whitegrid')

                pos_x = data_forces_and_pos[f'{sensorfoot}_pos_x'].dropna()
                pos_y = data_forces_and_pos[f'{sensorfoot}_pos_y'].dropna()
                pos_z = data_forces_and_pos[f'{sensorfoot}_pos_z'].dropna()

                ax = sn.lineplot(x = x_forces, y = data_forces_and_pos['force_x'], data=data_forces_and_pos)
                sn.lineplot(x = x_forces, y = data_forces_and_pos['force_y'], data=data_forces_and_pos, ax=ax)
                sn.lineplot(x = x_forces, y = data_forces_and_pos['force_z'], data=data_forces_and_pos, ax=ax)
                ax2 = ax.twiny()
                sn.lineplot(x = x_pos, y = pos_x, data=data_forces_and_pos, ax=ax2)
                sn.lineplot(x = x_pos, y = pos_y, data=data_forces_and_pos, ax=ax2)
                sn.lineplot(x = x_pos, y = pos_z, data=data_forces_and_pos, ax=ax2)

                plt.xlabel('frames')
                plt.ylabel(f'{run_number}_forces')

                fig1 = plt.gcf()
                fig1.savefig(os.path.join(output_path, f'{run_number}_force_pos_plot.png'))

                plt.show()

    return