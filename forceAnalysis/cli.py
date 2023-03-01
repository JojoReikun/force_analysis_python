import os
import click
from pathlib import Path

import forceAnalysis

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(invoke_without_command=True)
# @click.version_option()
@click.option('-v', '--verbose', is_flag=True, help='Verbose printing')
@click.pass_context
def main(ctx, verbose):
    if ctx.invoked_subcommand is None:
        click.echo('forceAnalysis')
        click.echo(main.get_help(ctx))

## DATA ASSEMBLY
##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('subject', default="magneto", help='subject which to assemble data for: either "magneto" or "lizards"')
@click.argument('date', default="all", help='date YYYY-MM-DD to choose single date only. Otherwise all dates will be used')

@click.pass_context


def assemble_force_data(_, *args, **kwargs):
    """Reads in the given list of .csv files for the subject and assembled the data.
    Arguments \n
    ---------- \n

    Options \n
    ---------- \n
    subject : string \n
    \tString either "lizards" or "magneto" \n
    date : string \n
    \tString as YYYY-MM-DD
    """
    from forceAnalysis.operations import assemble_data
    assemble_data.assemble(*args, **kwargs)


## DATA SUMMARY
##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.option('date', help='date YYYY-MM-DD the data collection table and trials were recorded on')
@click.pass_context

def create_summary_data(_, *args, **kwargs):
    """Reads in the given list of *assembled_meta.csv files for the given date and assembles all runs into a summary data sheet,
    taking the means of the 3 collected trials.
    Options \n
    ---------- \n
    date : string \n
    \tString as YYYY-MM-DD
    """
    from forceAnalysis.operations import create_summary_file
    create_summary_file.create_summary(*args, **kwargs)


## GAMMA FORCE PLATE DATA
##################################################################################
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option('date', help='date YYYY-MM-DD the trials were recorded on')
@click.pass_context
def gamma_forces(_, *args, **kwargs):
    """
    Forces with the gamma force plate were collected during the trials with Magneto in March/April 2021.
    Forces could only be collected for one foot at a time. The foot was noted in the trial notes (DataCollectionTable).
    Of the 3 trials, usually one FR and one HR foot were recorded. If foot didn't hit the force plate properly this
    was noted in the comments in the trial notes.
    To extract the correct force spike for the footstep onto the force plate, interactive matplotlib plotting is used.

    :return:
    """
    from forceAnalysis.operations import forces_gamma_magneto
    forces_gamma_magneto.extract_forces_gamma(*args, **kwargs)


## PLOT GOPRO AUDIO DATA
##################################################################################
@main.command(context_settings=CONTEXT_SETTINGS)
@click.option('date', help='date YYYY-MM-DD the trials were recorded on')
@click.pass_context
def gamma_forces(_, *args, **kwargs):
    """
    Plot the audio of the GoPro videos and save "audio" track as csv file with matching date in name.
    Names of GoPro videos corresponding to the trials are in magneto_climbing_gait/experiments in dataCollectionTable_all.xlsx

    :return:
    """
    from forceAnalysis.operations import gopro_audio_analysis
    gopro_audio_analysis.plot_gopro_audio(*args, **kwargs)


## PLOT HEATMAPS
##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.option('date', help='date YYYY-MM-DD the data collection table and trials were recorded on')
@click.pass_context

def create_summary_data_maps(_, *args, **kwargs):
    """Reads in the summary_data file of the given date and plots the heatmap defined for that date (depends on data collected)
    Options \n
    ---------- \n
    date : string \n
    \tString as YYYY-MM-DD
    """
    from forceAnalysis.operations import plot_landscapes_from_data
    plot_landscapes_from_data.plot_heatmaps(*args, **kwargs)



## PLOT FORCES:
##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('overwrite_plots',
              default=True,
              help='determines if plots should be created and saved. If True, plots that exist already will be overwritten.')
@click.pass_context


def plot_forces(_, *args, **kwargs):
    """Reads in the list of assembled.csv files and plots the force data
    Options \n
    ---------- \n
    overwrite_csv_files: boolean \n
    \tBoolean either True or False. Default: True. determine if to overwrite the plots
    """
    from forceAnalysis.operations import plot_forces
    plot_forces.plot_force_data(*args, **kwargs)


## PLOT IMU:
##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('overwrite_plots',
              default=True,
              help='determines if plots should be created and saved. If True, plots that exist already will be overwritten.')
@click.pass_context

def plot_imu(_, *args, **kwargs):
    """Reads in the list of assembled.csv files and plots the force data
    Options \n
    ---------- \n
    overwrite_csv_files: boolean \n
    \tBoolean either True or False. Default: True. determine if to overwrite the plots
    """
    from forceAnalysis.operations import plot_imu_data
    plot_imu_data.plot_imu(*args, **kwargs)


## PLOT SUMMARY DATA:
##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('overwrite_plots',
              default=True,
              help='determines if plots should be created and saved. If True, plots that exist already will be overwritten.')
@click.pass_context

def plot_summary(_, *args, **kwargs):
    """Reads in the list of assembled.csv files and plots the force data
    Options \n
    ---------- \n
    overwrite_csv_files: boolean \n
    \tBoolean either True or False. Default: True. determine if to overwrite the plots
    """
    from forceAnalysis.operations import plot_summary_data
    plot_summary_data.plot_summary(*args, **kwargs)


## PLOT FORCE AND POSITION DATA:
##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('overwrite_plots',
              default=True,
              help='determines if plots should be created and saved. If True, plots that exist already will be overwritten.')
@click.argument('smoothing',
              default=True,
              help='if smoothing is true the foot position data of the sensor foot will be smoothed.')
@click.argument('filtertype',
              default='savgol',
              help='sets the type of filter to use for smoothing. Available are: "butter", "fft", "savgol"')
@click.pass_context

def plot_force_and_position(_, *args, **kwargs):
    """Reads in the list of assembled.csv files and plots the force data
    Options \n
    ---------- \n
    overwrite_csv_files: boolean \n
    \tBoolean either True or False. Default: True. determine if to overwrite the plots
    """
    from forceAnalysis.operations import plot_force_and_position
    plot_force_and_position.plot_force_data_and_position_data(*args, **kwargs)
