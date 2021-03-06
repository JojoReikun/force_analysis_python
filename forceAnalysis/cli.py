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
@click.option('subject', help='subject which to assemble data for: either "magneto" or "lizards"')
@click.argument('overwrite_csv_files',
              default=True,
              help='determines if csv files should be created and saved. If True, plots that exist already will be overwritten.')
@click.pass_context


def assemble_force_data(_, *args, **kwargs):
    """Reads in the given list of .csv files for the subject and assembled the data.
    Arguments \n
    ---------- \n
    overwrite_csv_files: boolean \n
    \tBoolean either True or False. Default: True. determine if to overwrite the csv data files for every run

    Options \n
    ---------- \n
    subject : string \n
    \tString either "lizards" or "magneto" \n
    """
    from forceAnalysis.operations import assemble_data
    assemble_data.assemble(*args, **kwargs)


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
