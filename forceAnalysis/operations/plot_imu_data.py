def plot_imu(overwrite_plots):
    import matplotlib.pyplot as plt
    import seaborn as sn
    import pandas as pd
    import os.path
    from glob import glob
    from forceAnalysis.utils import auxiliaryfunctions


    if overwrite_plots == True:
        path = os.path.join(os.getcwd(), "assembled_csv")

        output_path = os.path.join(path, "imu_plots")
        auxiliaryfunctions.attempttomakefolder(output_path)

        if os.path.isdir(path):
            for file in glob(os.path.join(path, "*.csv")):
                data = pd.read_csv(file)
                data_imu = data[['imu_linacc_x', 'imu_linacc_y', 'imu_linacc_z']]
                print("data_imu: ", data_imu.head())

                run_number = file.rsplit(os.sep, 1)[1]
                run_number = run_number.split("_", 1)[0]

                colours = ['#e69239', '#80d5e8', '#b2e880']
                sn.set_palette(colours)
                sn.set_style('whitegrid')
                sn.lineplot(data=data_imu)
                plt.xlabel('frames')
                plt.ylabel(f'{run_number}_linacc')

                fig1 = plt.gcf()
                fig1.savefig(os.path.join(output_path, f'{run_number}_imu_plot.png'))

                plt.show()
