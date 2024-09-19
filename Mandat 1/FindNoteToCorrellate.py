import matplotlib.pyplot as plt
import RecordMicro
import PlayNotes

recorder = RecordMicro.RecordMicro()
playNotes = PlayNotes.PlayNotes()

for name in playNotes.dict_name_pos.keys():
    print(f"Time to learn note {name}")
    t, recording = recorder.record()
    norm_recording = RecordMicro.normalize(recording)
    recorder.find_highest_peak(t, norm_recording, filename=name)