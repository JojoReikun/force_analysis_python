import os

DEBUG = True and 'DEBUG' in os.environ and os.environ['DEBUG']
from forceAnalysis import DEBUG
from inspect import getmembers, isfunction

from forceAnalysis.utils import auxiliaryfunctions
from forceAnalysis import operations
from forceAnalysis.operations.assemble_data import assemble
from forceAnalysis.operations.create_summary_file import create_summary
from forceAnalysis.operations.forces_gamma_magneto import extract_forces_gamma
from forceAnalysis.operations.gopro_audio_analysis import plot_gopro_audio
from forceAnalysis.operations.gopro_audio_force_matching import match_audio_and_force

## for 28th Oct 2020 data collection:
from forceAnalysis.operations.plot_forces import plot_force_data
from forceAnalysis.operations.plot_imu_data import plot_imu
from forceAnalysis.operations.plot_summary_data import plot_summary
from forceAnalysis.operations.plot_force_and_position import plot_force_data_and_position_data
from forceAnalysis.operations.plot_landscapes_from_data import plot_heatmaps

print("forceAnalysis imported successfully. Now you can: \n")
print("-- assemble the trial data combining the Magneto sensor data, and trial note info")
print("use: >>forceAnalysis.assemble(subject, date) to do this.")
print("subject: >>magneto<<. date: >>YYYY-MM-DD<<")
print("make sure the >>time<< column in the dataCollectionSheet matches the time in string in the folder names!")

print("-- create a summary file for the selected date")
print("use: >>forceAnalysis.create_summary(date) to do this.")

print("-- extract the forces of the gamma force plate for the selected date")
print("use: >>forceAnalysis.extract_forces_gamma(date) to do this.")

print("-- plot the gopro audio data to detect Magneto's steps, and match it to the force data. Step-wise force details will be extracted")
print("use: >>forceAnalysis.plot_gopro_audio(date, gait) to do this.")