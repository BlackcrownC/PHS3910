import numpy as np
import os
from matplotlib import pyplot as plt

folder_path = 'Correlation'

for note in os.listdir(folder_path):
    note_folder = os.path.join(folder_path, note)
    for try_ in os.listdir(note_folder):
        data = np.load(os.path.join(folder_path, note, try_))
        new_data = data[::4]
    
        dir = 'correlation_v2'
        os.makedirs(f"{dir}\{note}", exist_ok=True)
        np.save(f"{dir}\{note}\{try_}", new_data)
        data_shape = new_data.shape
        print(f'Saved data as {dir}\{note}\{try_} with shape {data_shape}')

plt.plot(new_data)
plt.show()