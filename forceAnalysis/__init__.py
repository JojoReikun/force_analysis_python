import os

DEBUG = True and 'DEBUG' in os.environ and os.environ['DEBUG']
from forceAnalysis import DEBUG

from forceAnalysis.utils import auxiliaryfunctions
from forceAnalysis import operations
from forceAnalysis.operations.assemble_data import assemble
from forceAnalysis.operations.create_summary_file import create_summary
from forceAnalysis.operations.plot_forces import plot_force_data
from forceAnalysis.operations.plot_imu_data import plot_imu
from forceAnalysis.operations.plot_summary_data import plot_summary
from forceAnalysis.operations.plot_force_and_position import plot_force_data_and_position_data
from forceAnalysis.operations.plot_landscapes_from_data import plot_heatmaps