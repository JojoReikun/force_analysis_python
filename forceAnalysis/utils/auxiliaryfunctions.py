def get_path_of_folder():
    ### IMPORTS
    import os
    from tkinter import filedialog, Tk

    root = Tk()


    current_path = os.getcwd()
    folder_path = filedialog.askdirectory(parent=root, initialdir=current_path,
                                          title="Please select folder with data csv files")
    root.withdraw()  # to hide tkinter window
    return folder_path


def define_colours():
    colour_dict = {'fore-aft': "#548235",   # green
                   'lateral': "#7030A0",    # purple
                   'normal': "#BF9000"}     # sand
    return colour_dict


def attempttomakefolder(foldername, recursive=False):
    ''' Attempts to create a folder with specified name. Does nothing if it already exists. '''
    import os
    try:
        os.path.isdir(foldername)
    except TypeError: #https://www.python.org/dev/peps/pep-0519/
        foldername=os.fspath(foldername) #https://github.com/AlexEMG/DeepLabCut/issues/105 (windows)

    if os.path.isdir(foldername):
        #print(foldername, " already exists!")
        pass
    else:
        if recursive:
            os.makedirs(foldername)
        else:
            os.mkdir(foldername)


def get_sensorfoot_for_run(run_number):
    "takes a string containing the run number and returns the respective sensorfoot for this run"
    sensorfoot_dict = {(1, 16):"FR",
                       (16, 34):"HR"}

    #print("run number: ", run_number, type(run_number))
    # extract the run number from the string:
    run_int = int(''.join(filter(lambda i: i.isdigit(), run_number)))
    #print("run_int: ", run_int, type(run_int))

    sensorfoot_of_run = 0
    for i in range(len(sensorfoot_dict.keys())):
        key = list(sensorfoot_dict.keys())[i]
        #print("key: ", key)
        #print(range(key[0], key[1]))
        if run_int in range(key[0], key[1]):
            sensorfoot_of_run = sensorfoot_dict[key]

    if sensorfoot_of_run == 0:
        print("Run number has no responding sensorfoot")

    #print("aux funcs, sensorfoot: ", sensorfoot_of_run)
    return sensorfoot_of_run