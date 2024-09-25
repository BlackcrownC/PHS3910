import RecordMicro
import PlayNotes
import os

recorder = RecordMicro.RecordMicro()
playNotes = PlayNotes.PlayNotes()

for name in playNotes.dict_name_pos.keys():
    print(f"Time to learn note {name}")

    # Créer le répertoire s'il n'existe pas déjà
    os.makedirs(name, exist_ok=True)

    t, recording = recorder.record()
    norm_recording = RecordMicro.normalize(recording)
    peak = recorder.find_highest_peak(t, norm_recording, filename=name)
    recorder.save_peak(peak, f"{name}/1")