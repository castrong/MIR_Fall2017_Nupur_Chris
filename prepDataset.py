import mido
import random
from mido import Message, MidiFile, MidiTrack


def printMidi(fileName):
	midiToPlay = MidiFile(fileName)
	for track in midiToPlay.tracks:
	    for msg in track:
	        print(msg)

def onlynote(inputFileName, outputFileName, pitchShift, timeShift, timeScale):
	orig = MidiFile(inputFileName)
	mid = MidiFile()

	for tr in orig.tracks:
		track = MidiTrack()
		mid.tracks.append(track)
#<meta message track_name name='Grand Piano' time=0>

#		msg = Message()
		msg = Message('note_on', note=0, velocity=0, time=timeShift)
		track.append(msg)

		for msg in tr:
			if msg.type == 'note_on':
				msg.time = round(msg.time * timeScale)
				msg.note = msg.note + pitchShift
				track.append(msg)

	print(mid.ticks_per_beat)

	mid.save(outputFileName)

onlynote('Godowtsai Dataset/Chopin/chopin_op10_e01.mid', 'Output Midi/chopin_op10_e01_no_tempo.mid', 0, 0,1)
printMidi('Output Midi/chopin_op10_e01_no_tempo.mid')
onlynote('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e01.mid', 'Output Midi/godowsky_v1_chopin_op10_e01_no_tempo.mid', 0, 0, 1)

onlynote('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e01.mid', 'Output Midi/godowsky_v1_chopin_op10_e01_shifted.mid', -12, 357, 0.3495)

#printMidi('Godowtsai Dataset/Mechanical Godowsky/godowsky_v1_chopin_op10_e01.mid')
#printMidi('Godowtsai Dataset/Chopin/chopin_op10_e01.mid')
