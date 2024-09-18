import os

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import RecordMicro

# ouvrir les .npy dans correlation

notes = []
names = []
# find all files in Correlation folder
for filename in os.listdir('correlation'):
    if filename.endswith(".npy"):
        notes.append(np.load(f'correlation/{filename}'))
        names.append(filename)

# Enregistrer un signal
recorder = RecordMicro.RecordMicro(seconds=5, fs=44100, default=True)
t, myrecording = recorder.record()
myrecording = recorder.normalize(myrecording)
peak = recorder.find_highest_peak(t, myrecording, filename='A')

# Corrélation

correlations = []
for n in notes:
    correlations.append(np.correlate(peak, n, mode='full'))

for i, c in enumerate(correlations):
    plt.plot(c)
    plt.title(names[i])
    plt.show()
