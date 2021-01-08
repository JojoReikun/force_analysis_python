import os

DEBUG = True and 'DEBUG' in os.environ and os.environ['DEBUG']
from forceAnalysis import DEBUG

from forceAnalysis.utils import auxiliaryfunctions
from forceAnalysis import operations
from forceAnalysis.operations.assemble_data import assemble
from forceAnalysis.operations.plot_forces import plot_force_data
from forceAnalysis.operations.plot_imu_data import plot_imu
