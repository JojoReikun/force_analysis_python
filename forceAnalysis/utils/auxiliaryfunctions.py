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
