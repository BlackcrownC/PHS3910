import os

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import RecordMicro

dict_name_pos = {
    "A": (0, 0),
    "C": (1, 0),
    "B": (0, 1),
    "D": (1, 1),
}

# Find max of dict positions
rows = max([p[0] for p in dict_name_pos.values()]) + 1
cols = max([p[1] for p in dict_name_pos.values()]) + 1

corr_matrix = np.zeros((rows, cols))
names_matrix = np.empty((rows, cols), dtype=str)

# Enregistrer un signal et garder le peak
recorder = RecordMicro.RecordMicro()
t, recording = recorder.record()
norm_recording = recorder.normalize(recording)
peak = recorder.find_highest_peak(t, norm_recording)
# peak = recorder.find_highest_peak(t, norm_recording, filename='test_to_correll')

# find all .npy files in Correlation folder
npy_files = [filename for filename in os.listdir('correlation') if filename.endswith('.npy')]

# Check if the number of files in the folder is the same as the number of notes in the dict
if len(npy_files) != len(dict_name_pos):
    raise ValueError(f"Number of files in correlation folder ({len(npy_files)}) is different from the number of notes in the dict ({len(dict_name_pos)})")

# Correlate the peak with each note
for filename in npy_files:
    note = np.load(f'correlation/{filename}')
    name = filename[:-4] # get the name of the file without the extension

    # Correlate the peak with the note
    # J'imagine que "same" est le meilleur mode???
    corr = np.correlate(peak, note, mode='same')
    max_corr = np.max(corr)
    # plt.plot(corr)
    # plt.title(names[i])
    # plt.show()
    print(name, max_corr)
    # associate the name of the file with the coordinates of the heat map and the max of the correlation
    if dict_name_pos[name] is None:
        print(f"Error: {name} not in dict_name_pos but is in the files (trained model)")
        break
        # raise ValueError(f"{name} not in dict_name_pos but is in the files (trained model)")

    corr_matrix[dict_name_pos[name]] = max_corr
    names_matrix[dict_name_pos[name]] = name

# Heat map of the correlation matrix
plt.imshow(corr_matrix, cmap='binary', interpolation='nearest')
plt.colorbar()
plt.xticks(range(0, cols))
plt.yticks(range(0, rows))
plt.xlabel('X grid')
plt.ylabel('Y grid')
# put xlabel on the top
plt.gca().xaxis.set_ticks_position('top')
plt.title('Heat map of the correlation matrix')

# Ajouter les lettres aux positions correspondantes
for i in range(names_matrix.shape[0]):
    for j in range(names_matrix.shape[1]):
        plt.text(j, i, names_matrix[i, j], ha='center', va='center', color='red')

plt.show()