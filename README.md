# force_analysis_python
force analysis for Magneto and Lizards

This progam enables the user to perform experimental data assembly for Magneto force trials and Lizard force trials (coming soon).

## Usage:
In the pycharm console or the virt env of the project:
```
>> import forceAnalysis
```
Then different commands can be executed:
## 1) Data assembly:
Within this module the data from the Magneto internal sensors are combined with the trial notes data, which include climbed distance etc.
***>Soon***: The forces collected with the gamma force plate can also be added to the combined data sheets if desired.

#### Note: date and subject are optional. If date is left blank, all data trials over all dates will be used. If subject is left blank, magneto will be used by default.
```
>> forceAnalysis.assemble(subject="magneto", date="YYYY-MM-DD")  # "magneto" or "lizards"
```
### For assemble(): 
- By default the data for **magneto** will be looked at. If instead data for lizards should be assembled, subject has to be changed to "lizards" (not yet functional) 
- The date refers to the date the trials were collected on. The dataCollectionTable_date.xlsx will be used for this trial date.

Inside assemble the data collection notes will be combined with the actual sensor results from Magnetos sensors.
The raw data is stored as .bag files and has to be converted to .csv before executing this script. The **bag_to_csv.py** script
does this. The sensor data of interest and the respective .bag file topics (or csv files) are defined within the code,
currently defined: IMU data, foot positions, internal force sensor data, voltage, current and power.

Magneto sensor data collected with different sample frequencies are aligned using the ROS time stamp. 

##### Output:
An "_assembled.csv" file will be created for each run with the combined sensor data of Magneto.
Further an "_assembled_meta.csv" file will be created which has the trial run info from the dataCollectionTable added to it.

## 2) Data summary:
This function combines the individual "_assembled_meta.csv" files for the selected date into a summary file. 
Means for the usually n=3 trials/configuration will be used.
- needs: The "_assembled_meta.csv" files

```
>> forceAnalysis.create_summary(date="YYYY-MM-DD") 
```

##### Output:
A summary file stored in python_force_analysis/result_files/YYYY-MM-DD/summary_data

## 3) Forces Gamma Magneto:
This step requires a fair bit of manual work by the user. The goal is to investigate the force plots for each run for the selected trial date one by one,
and select the force interval that contains the foot on the force plate. To go through this step:
Prepare a new excel spreadsheet called: **"{date}_gammaForces.csv"** in the folder:
...\magneto_climbing_gait\experiments\magnetoAtUSC_gammaForces\{date}_forcesGamma
It should look like this:
- green shaded columns can be copied from the respective summary data sheet ("{date}_summary_data.csv") in python_force_analysis result_files folder
- ornage shaded columns need to be added and filled in while plotting individual run force tracks. Write "na" if no foot is on the force plate (see comments)
![](assets/excel_extract_gamma_forces.PNG)


## 4) Plot audio track of GoPro to detect steps Magneto:
To analyse the gamma force data properly, we need to know when Magneto moves the feet. Because Magneto
only moves 1 foot at any time, the foot on the force plate remains there while the 3 other feet do their step
before it is lifted off the force plate. 
Therefore, the idea is to plot the audio track of the GoPro to match the "clonk" spiked of the 
Magnet feet when attaching to the steel track with the force Data. Once the steps are matched to the force recording,
we can see what happens to the forces during each step. For the force Data we know
which foot attached to the force plate and in which step cycle as well as when the force measurement was stopped.
Sketch of idea:
![](assets/audiospikes_forcetrack_overlay_idea.png)


```
>>> forceAnalysis.plot_gopro_audio(date, gait)
i.e.: >>> forceAnalysis.plot_gopro_audio("07-04-2021", 2)
```
We need to know which GoPro video belongs to which run, hence the user will have to add this information into the previously 
generated csv file: "{date}_gammaForces.csv". Add columns "gopro_video_file" and "audiofile", fill in as shown below:

### -->> Step 1:
**- needs: added columns "gopro_video_file" and "audiofile" to "{date}_gammaForces.csv" to know which GoPro videos belong to which run**

As a first step the gopro videos for the selected date are loaded and the audio track is exported 
as a separate .wav file with the same filename otherwise.
Then the .wav file is read in and plotted and then the spikes are detected using the "find_peaks" function
from scipy.signal library.

This step is skipped if the audio files are already present.

### -->> Step 2:
As a second step the module will then check if a "audio_wave_start_s" and "audio_wave_end_s" column are already existant in the respective 
**"{date}_gammaForces.csv"** sheet. If not user will be asked to add them in manually first (see below how to) before re-executing this 
command.

Because spikes of e.g. Magneto being put onto the steel track and being taken off might get detected as well,
to only use the "step spikes" the user has to use the plots of the audio tracks to manually add
a start and end column to the excel sheet **"{date}_gammaForces.csv"** as per below:
start and end frame don't have to be exact, in the example it could be start = 25, end = 95.
![](assets/example_gopro_audio_plot.png)
![](assets/excel_gopro_audio.PNG)

Further add a column "comments_audio" to note which audio tracks are "clean" and which ones might have some 
missing spikes because spike was below cut-off. Also note which tracks are untidy and not worth to include 
unless not enough data overall. Use these comments to add another column, which inidcates for the script the "status" 
of the trial and therefore what to do with it, when re-reading in the excel sheet:
![](assets/excel_gopro_audio_status.PNG)

### Status codes explained:
- ![#f03c15](https://placehold.co/15x15/f03c15/f03c15.png) `Status Code: red`: status is "red":
  - if there is no foot on the FP (e.g. column start_stepon = na)
  - if the spikes are too untidy and extra post processing would take a while
- ![#f03c15](https://placehold.co/15x15/c98300/c98300.png) `Status Code: orange`: status is "orange":
  - if nth spike was not detected because it was below the cut-off value "height" in the function arguments of find_peaks().
  Use the find_peaks function again only within the manually selected interval with a lower height to detect missing peaks 
- ![#f03c15](https://placehold.co/15x15/00c943/00c943.png) `Status Code: green`: status is "green": 
  - if all 12 steps were detected and no other missing or false peaks were detected.

### -->> Step 3:
As a third step, the start and end markers are then read in again when executing the same command in the console.
Depending on the status code of the trial the audio track is treated in a different way.

For all status orange trials, the selected audio interval is reanalysed to find the missing peaks. A "status_refined"
column is added to the "{date}_gammaForces_step3.csv" file which needs to be updated depending on how the new plots look, before proceeding to the 4th step, where the 
found audio spikes of the steps are matched to the force data. Further a "foot_on_fp" column needs to be added manually.
This column contains the integer of the foot step which is on the force plate. Careful!!! This depends on the gait pf the trial!
This file has to be saved as "{date}_gammaForces_step4.csv"
![](assets/spreadsheet_step4_example.PNG)

The spikes and their respective frames are extracted as a dict for spikes in the given frame interval only.
Plots are saved in the gopro video folder in a new "plot" directory. Look through them to adjust the status_refined in the "{date}_gammaForces_step3.csv" file:


**Note that 11th spike is still missing in the left plot, but 8th has now been found!**
Spike detection is done using a minimal spike interval width and a cut-off height, for reanalysing orange stati only the height is changed.
This step might have to be re-run again, if the width is not ideal to find all missing spikes, hence increase tolerance (right plot)
![](assets/refined_goproaudio_plot_example.png)


### -->> Step 4:
- **needs: "{date}_gammaForces_step4.csv"**
- **audio peak dictionary created in step3**

As a 4th Step: Audio data of status green files is matched to the respective force tracks. 
Two ways to do so were coded in the proces of figuring out the best way to match the differing sample rates of force and audio data:
With interpolation to match sample rates or without interpolation using frame rate to time to other frame rate conversions. This 
can be chosen in the respective module within the function match_audio_and_force() by setting the bool value of interpolation = True/False.

The audio signal is trimmed to the relevant spikes ...

Plots of the matches trials are saved for user control and visual data analysis, example below:
![](assets/GH017439_forces_and_audiopeaks_noInterp.jpg)


## Magneto
The sensors in Magneto are orientated as follows:
![](assets/Magneto_Orientations.jpg)

In the data assembly files (for every run), "static" data (e.g. velocity, foot which sensor was mounted in, etc.) 
and the timestep wise collected data (e.g. forces, imu data or feet positions) are accumulated.

#### Magneto gait patterns:
The standard gait pattern for Magneto follows the order of gait1 - a cyclic pattern.
We have modified this gait pattern to follow a more lizard-like order, gait2 - a diagonal gait pattern, yet still only moving 1 foot at a time.
![](assets/magneto_gaits.PNG)



```
>> forceAnalysis.plot_forces(overwrite_plots=True)
>> forceAnalysis.plot_imu(overwrite_plots=True)
```