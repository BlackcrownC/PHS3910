import os

import numpy as np
import matplotlib.pyplot as plt
import RecordMicro


def get_npy_files(folder='correlation'):
    return [filename for filename in os.listdir(folder) if filename.endswith('.npy')]


class PlayNotes:
    def __init__(self):
        self._npy_files = None
        self._rows = None
        self._cols = None

        self.dict_name_pos = {
            "A": (0, 0),
            "C": (1, 0),
            "B": (0, 1),
            "D": (1, 1),
        }

    @property
    def npy_files(self):
        if self._npy_files is None:
            self._npy_files = get_npy_files()
            self.check_for_files()
        return self._npy_files

    @property
    def rows(self): # Find max of dict positions
        if self._rows is None:
            self._rows = max([p[0] for p in self.dict_name_pos.values()]) + 1
        return self._rows

    @property
    def cols(self): # Find max of dict positions
        if self._cols is None:
            self._cols = max([p[1] for p in self.dict_name_pos.values()]) + 1
        return self._cols

    def check_for_files(self):
        if len(self.npy_files) != len(self.dict_name_pos):
            raise ValueError(f"Number of files in correlation folder ({len(self.npy_files)}) is different from the number of notes in the dict ({len(self.dict_name_pos)})")

    def correlate_peak_with_notes(self, peak):
        corr_matrix, names_matrix = self.create_matrices()
        for filename in self.npy_files:
            note = np.load(f'correlation/{filename}')
            name = filename[:-4]  # get the name of the file without the extension

            # Correlate the peak with the note
            # J'imagine que "same" est le meilleur mode???
            corr = np.correlate(peak, note, mode='same')
            max_corr = np.max(corr)
            # plt.plot(corr)
            # plt.title(names[i])
            # plt.show()
            print(name, max_corr)
            # associate the name of the file with the coordinates of the heat map and the max of the correlation
            if self.dict_name_pos[name] is None:
                print(f"Error: {name} not in dict_name_pos but is in the files (trained model)")
                break
                # raise ValueError(f"{name} not in dict_name_pos but is in the files (trained model)")

            corr_matrix[self.dict_name_pos[name]] = max_corr
            names_matrix[self.dict_name_pos[name]] = name
        return corr_matrix, names_matrix

    def get_highest_correlation(self, peak):
        names = []
        max_corrs = []
        for filename in self.npy_files:
            note = np.load(f'correlation/{filename}')
            name = filename[:-4]  # get the name of the file without the extension

            # Correlate the peak with the note
            # J'imagine que "same" est le meilleur mode???
            corr = np.correlate(peak, note, mode='same')
            max_corr = np.max(corr)
            names.append(name)
            max_corrs.append(max_corr)
        # get the name of the note with the highest correlation
        highest_correlation = max_corrs.index(max(max_corrs))
        return names[highest_correlation]

    # surement à optimiser pour seulement avoir à le faire une fois
    def create_matrices(self):
        corr_matrix = np.zeros((self.rows, self.cols))
        names_matrix = np.empty((self.rows, self.cols), dtype=str)

        return corr_matrix, names_matrix

    def show_heat_map(self, corr_matrix, names_matrix):
        # Heat map of the correlation matrix
        plt.imshow(corr_matrix, cmap='binary', interpolation='nearest')
        plt.colorbar()
        plt.xticks(range(0, self.cols))
        plt.yticks(range(0, self.rows))
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


# Enregistrer un signal et garder le peak
recorder = RecordMicro.RecordMicro()
t, recording = recorder.record()
norm_recording = RecordMicro.normalize(recording)
peak = recorder.find_highest_peak(t, norm_recording)
# peak = recorder.find_highest_peak(t, norm_recording, filename='test_to_correl')


notesPlayer = PlayNotes()
corr_matrix, names_matrix = notesPlayer.correlate_peak_with_notes(peak)
notesPlayer.show_heat_map(corr_matrix, names_matrix)