import wfdb as wf # waveform database package used for reading, writing, and processing wfdb signals and annotations
from wfdb import processing # for finding rpeaks to calculate heart bpm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk 
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import ttk
from os import listdir

def plot_ekg():
    # figure that contains the ekgs
    global canvas, toolbar, ekg1_bpm_label, ekg2_bpm_label, pathologies, pathology_label
    figure.clf()
    patient = str(dropdown.current() + 1)
    # read data
    if dropdown.current() + 1 < 10:
        ekg_data = read_data('0'+patient)
    else:
        ekg_data = read_data(patient)
    time = np.linspace(0, len(ekg_data)/fs, num=len(ekg_data))
    ekg1_x = ekg_data[0:, 1]
    ekg2_x = ekg_data[0:, 2]

    # find rpeaks
    rpeaks = processing.xqrs_detect(ekg1_x, fs, verbose=False)
    # lead 1 ekg setup
    ekg1 = figure.add_subplot(211)
    ekg1.set_xlim(0, 5)
    ekg1.set_ylim(np.min(ekg1_x), np.max(ekg1_x))
    ekg1.set_title('LEAD I')
    ekg1.set_xlabel('TIME(S)')
    ekg1.set_ylabel('MILLIVOLTS(mV)')
    ekg1.plot(time, ekg1_x)
    ekg1.plot(rpeaks / fs, ekg1_x[rpeaks], 'ro')
    ekg1_bpm = round(np.mean(rpeaks) / fs)
    del rpeaks
    # lead 2 ekg setup
    rpeaks = processing.xqrs_detect(ekg2_x, fs, verbose=False)
    ekg2 = figure.add_subplot(212)
    ekg2.set_xlim(0, 5)
    ekg2.set_ylim(np.min(ekg2_x), np.max(ekg2_x))
    ekg2.set_title('LEAD II')
    ekg2.set_xlabel('TIME(S)')
    ekg2.set_ylabel('MILLIVOLTS(mV)')
    ekg2.plot(time, ekg2_x)
    ekg2.plot(rpeaks / fs, ekg2_x[rpeaks], 'ro')
    ekg2_bpm = round(np.mean(rpeaks) / fs)
    # add padding between the subplots
    figure.tight_layout()
    # pack tk elements
    pathology_label.destroy()
    ekg1_bpm_label.destroy()
    ekg2_bpm_label.destroy()
    pathology_label = Label(master = window, text = f'PATHOLOGY: {pathologies[int(patient)-1]}',font=('Arial',16))
    ekg1_bpm_label = Label(master = window, text = f'EKG1 {ekg1_bpm} BPM', font=('Arial',16))
    ekg2_bpm_label = Label(master = window, text = f'EKG2 {ekg2_bpm} BPM', font=('Arial',16))
    pathology_label.pack()
    ekg2_bpm_label.pack()
    ekg1_bpm_label.pack()
    # tkinter canvas setup
    canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(figure, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    # integrate matlab toolbar in the tkinter window
    toolbar.destroy()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas.get_tk_widget().pack()

def read_data(patient):
    global fs
    # data paths
    data_path = 'ProgramePython/proiect1/human_data/' + patient
    csv_path = 'ProgramePython/proiect1/01.csv'
    record = wf.rdsamp(data_path)
    # sampling frequency(number of data points recorded per second)
    fs = record[1]['fs']
    df = pd.DataFrame(record[0], columns=record[1]['sig_name'])
    df.to_csv(csv_path)
    csv_data = pd.read_csv(csv_path, sep=',', header=None)
    #convert from str to float
    ekg_data = np.asarray(csv_data[1:], dtype="float")
    return ekg_data

def read_pathologies():
    pathologies_file = open('ProgramePython/proiect1/human_data/pathologies.txt', 'r')
    pathologies_data = pathologies_file.readlines()
    pathologies = []
    for line in pathologies_data:
        line_copy = line.split()
        pathologies.append(line_copy[1])
    pathologies.pop(0)
    pathologies_file.close()
    return pathologies

# tkinter setup
window = Tk()
window.title('EKG Viewer')
window.geometry('1280x720')
click = StringVar()
figure = Figure(figsize=(6, 4), dpi=100)
canvas = FigureCanvasTkAgg(figure, master=window)
toolbar = NavigationToolbar2Tk(canvas, window) 
pathology_label = Label(master = window, text = '')
ekg1_bpm_label = Label(master = window, text = '')
ekg2_bpm_label = Label(master = window, text = '')

# populating the dropdown list with 50 human patients
counter = 0
for file in listdir('ProgramePython/proiect1/human_data'):
    if file.endswith('.dat'):
        counter += 1
pathologies = read_pathologies()
patients = [f'Patient {i}' for i in range(1, counter + 1)]
dropdown = ttk.Combobox(window, width=25, textvariable = click)
dropdown['values'] = patients
dropdown.current(0)
fs = 0

label = Label(window, text = 'SELECT PATIENT')  
plot_button = Button(master=window, command=plot_ekg, height = 4, width = 6, text = 'PLOT')

# pack the widgets in the window
dropdown.pack()
label.pack()
plot_button.pack()

window.mainloop()