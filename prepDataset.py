import mido
import random
from mido import Message, MidiFile, MidiTrack

orig = MidiFile('Godowtsai Dataset/Mechanical Godowsky/godowsky_v1_chopin_op10_e01.mid')


def printMidi(midiName):
	midiToPlay = MidiFile(midiName)
	for track in midiToPlay.tracks:
	    for msg in track:
	        print(msg)

def onlynote(pitchShift, timeScale):
	mid = MidiFile()

	for tr in orig.tracks:
		track = MidiTrack()
		mid.tracks.append(track)
		for msg in tr:
			msg.time = round(msg.time * timeScale)
			if msg.type == 'note_on':
				msg.note = msg.note + pitchShift
			track.append(msg)

	mid.save('Output Midi/godowsky_v1_chopin_op10_e01_only_note.mid')

onlynote(-12,1.333)

#printMidi('Godowtsai Dataset/Mechanical Godowsky/godowsky_v1_chopin_op10_e01.mid')
printMidi('Godowtsai Dataset/Possibly Mechanical Chopin/chopin_op10_e01.mid')