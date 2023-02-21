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
currently working on this...


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