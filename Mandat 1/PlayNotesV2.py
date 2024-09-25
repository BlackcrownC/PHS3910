import os

import numpy as np
import matplotlib.pyplot as plt
import RecordMicro


def get_npy_files(folder='correlation'):
    return [filename for filename in os.listdir(folder) if filename.endswith('.npy')]

def create_key_name(number_of_slices):
    key_names = ["C4", "C-4", "D4", "D-4", "E4", "F4", "F-4", "G4", "G-4", "A4", "A-4", "B4", "C5"]
    names_sliced = []

    for key_name in key_names:
        if key_name.__contains__('-'):
            names_sliced.append(key_name)
            break
        for i in range(1, number_of_slices + 1):
            names_sliced.append(f"{key_name}_{i}")
    return names_sliced

class PlayNotes:
    def __init__(self):
        self._npy_files = None

        self.keys_name = create_key_name(2)

    @property
    def npy_files(self):
        if self._npy_files is None:
            self._npy_files = get_npy_files()
            self.check_for_files()
        return self._npy_files

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


if __name__ == '__main__':
    # Enregistrer un signal et garder le peak
    recorder = RecordMicro.RecordMicro()
    t, recording = recorder.record()
    norm_recording = RecordMicro.normalize(recording)
    peak = recorder.find_highest_peak(t, norm_recording)
    # peak = recorder.find_highest_peak(t, norm_recording, filename='test_to_correl')

    notesPlayer = PlayNotes()
    corr_matrix, names_matrix = notesPlayer.correlate_peak_with_notes(peak)
    notesPlayer.show_heat_map(corr_matrix, names_matrix)