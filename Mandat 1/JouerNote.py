import numpy as np 
import os
import pygame

def jouer_note(note, folder_path) : 
    file_name = None
    if note[1] == '-':
        file_name = f"{note[0].lower() + '-' + note[2]}.wav"

    elif note[2] == '_':
        file_name = f"{note[:2].lower()}.wav"

    if file_name is None:
        print('wtf')
        return
    
    file_path = os.path.join(folder_path, file_name)
    print(file_name)
    print(file_path)
    if not os.path.isfile(file_path):
        print(f"Error: The file for note '{note}' does not exist in the folder.")
        return

     # Initialize pygame mixer
    pygame.mixer.init()
    
    # Load and play the wav file
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    
    # Wait until the music finishes playing
    while pygame.mixer.music.get_busy():
        continue
    print(f"Playing note: {note}")

if __name__ == "__main__" : 
    folder = 'Wav-Notes'
    note = input("Enter the note you want to play (e.g., C4_1, D4_2, C-4): ").strip()
    jouer_note(note, folder)