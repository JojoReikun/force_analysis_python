def plot_force_data(overwrite_plots):
    import matplotlib.pyplot as plt
    import seaborn as sn
    import pandas as pd
    import os.path
    from glob import glob
    from forceAnalysis.utils import auxiliaryfunctions


    if overwrite_plots == True:
        path = os.path.join(os.getcwd(), "assembled_csv")

        output_path = os.path.join(path, "force_plots")
        auxiliaryfunctions.attempttomakefolder(output_path)

        if os.path.isdir(path):
            for file in glob(os.path.join(path, "*.csv")):
                data = pd.read_csv(file)
                data_forces = data[['force_x', 'force_y', 'force_z']]
                print("data_forces: ", data_forces.head())

                run_number = file.rsplit(os.sep, 1)[1]
                run_number = run_number.split("_", 1)[0]

                colours = ['#e3433d', '#0b6ade', '#5bdea5']
                sn.set_palette(colours)
                sn.set_style('whitegrid')
                sn.lineplot(data=data_forces)
                plt.xlabel('frames')
                plt.ylabel(f'{run_number}_forces')

                fig1 = plt.gcf()
                fig1.savefig(os.path.join(output_path, f'{run_number}_forceplot_plot.png'))

                plt.show()
