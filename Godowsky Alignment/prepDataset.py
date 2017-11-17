import mido
import random
from mido import Message, MidiFile, MidiTrack

import pretty_midi


def printMidi(fileName):
	midiToPlay = MidiFile(fileName)
	for track in midiToPlay.tracks:
	    for msg in track:
	        print(msg)

def onlyNote(inputFileName, outputFileName, shiftFront):
	orig = MidiFile(inputFileName)
	mid = MidiFile()

	for tr in orig.tracks:
		track = MidiTrack()
		mid.tracks.append(track)
		#<meta message track_name name='Grand Piano' time=0>

		# msg = Message('note_on', note=0, velocity=0, time=timeShift)
		# track.append(msg)

		for msg in tr:
			if msg.type == 'note_on' or msg.type == 'note_off':
				if msg.time != shiftFront:
					track.append(msg)
	mid.save(outputFileName)

def shiftAndScale(inputFileName, outputFileName, pitchShift, timeScale):
	orig = MidiFile(inputFileName)
	mid = MidiFile()

	for tr in orig.tracks:
		track = MidiTrack()
		mid.tracks.append(track)
#<meta message track_name name='Grand Piano' time=0>
		
		# time=0 could be replaced be time=timeShift if necessary
		msg = Message('note_on', note=0, velocity=0, time=0)
		track.append(msg)

		for msg in tr:
			if msg.type == 'note_on':
				msg.time = round(msg.time * timeScale)
				msg.note = msg.note + pitchShift
				track.append(msg)
	mid.save(outputFileName)

'''
Collapses different MIDI tracks (or "Instruments" by PrettyMIDI language) into a single track,
and then shifts the track so that there is no silence at the beginning of the track.
'''
def preprocessFile(inputFileName, outputFileName):
	# Load MIDI file into PrettyMIDI object
	midi_data = pretty_midi.PrettyMIDI(inputFileName)

	# Make a new PrettyMIDI object for the modified file
	modified_data = pretty_midi.PrettyMIDI()
	piano = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program('Acoustic Grand Piano'))
	modified_data.instruments.append(piano)

	for instrument in midi_data.instruments:
		for note in instrument.notes:
			piano.notes.append(note)

	onsets = modified_data.instruments[0].get_onsets()
	if onsets[0] > 0:
		for note in modified_data.instruments[0].notes:
			note.start = note.start - onsets[0]
			note.end = note.end - onsets[0]

	print(modified_data.get_end_time())
	modified_data.write(outputFileName)

'''
Take in processed file (one track, no initial silence)

TODO: pitch shift
'''
def scalePiece(inputFileName, outputFileName, timeScale, pitchShift):
	# Load MIDI file into PrettyMIDI object
	midi_data = pretty_midi.PrettyMIDI(inputFileName)

	for instrument in midi_data.instruments:
		for note in instrument.notes:
			note.start = note.start * timeScale
			note.end = note.end * timeScale
			note.pitch = note.pitch + pitchShift

	midi_data.write(outputFileName)

PATH_TO_DATASET = 'Godowtsai Dataset/'
PATH_TO_PROCESSED_FILES = 'Output Midi/Processed/'
LIST_TO_PROCESS = [
	'Chopin/chopin_op10_e01.mid',
	'Chopin/chopin_op10_e02.mid', 
	'Chopin/chopin_op10_e03.mid',
	'Chopin/chopin_op10_e04.mid', 
	'Chopin/chopin_op10_e05.mid', 
	'Chopin/chopin_op10_e06.mid', 
	'Chopin/chopin_op10_e07.mid', 
	'Chopin/chopin_op10_e08.mid', 
	'Chopin/chopin_op10_e09.mid', 
	'Chopin/chopin_op10_e10.mid', 
	'Chopin/chopin_op10_e11.mid', 
	'Chopin/chopin_op10_e12.mid', 
	'Chopin/chopin_op25_e01.mid', 
	'Chopin/chopin_op25_e02.mid', 
	'Chopin/chopin_op25_e03.mid', 
	'Chopin/chopin_op25_e04.mid', 
	'Chopin/chopin_op25_e05.mid', 
	'Chopin/chopin_op25_e06.mid', 
	'Chopin/chopin_op25_e07.mid', 
	'Chopin/chopin_op25_e08.mid', 
	'Chopin/chopin_op25_e09.mid',
	'Chopin/chopin_op25_e10.mid',
	'Chopin/chopin_op25_e11.mid', 
	'Chopin/chopin_op25_e12.mid',
	'Godowsky/godowsky_v1_chopin_op10_e01.mid',
	'Godowsky/godowsky_v1_chopin_op10_e02.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e03.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e04.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e05.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e06.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e07.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e08.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e09.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e10.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e11.mid', 
	'Godowsky/godowsky_v1_chopin_op10_e12.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e01.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e02.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e03.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e04.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e05.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e06.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e08.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e09.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e10.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e11.mid', 
	'Godowsky/godowsky_v1_chopin_op25_e12.mid', 
	'Godowsky/godowsky_v2_chopin_op10_e01.mid', 
	'Godowsky/godowsky_v2_chopin_op10_e02.mid', 
	'Godowsky/godowsky_v2_chopin_op10_e05.mid', 
	'Godowsky/godowsky_v2_chopin_op10_e07.mid', 
	'Godowsky/godowsky_v2_chopin_op10_e08.mid', 
	'Godowsky/godowsky_v2_chopin_op10_e09.mid', 
	'Godowsky/godowsky_v2_chopin_op10_e10.mid', 
	'Godowsky/godowsky_v2_chopin_op25_e01.mid', 
	'Godowsky/godowsky_v2_chopin_op25_e02.mid', 
	'Godowsky/godowsky_v2_chopin_op25_e03.mid', 
	'Godowsky/godowsky_v2_chopin_op25_e04.mid', 
	'Godowsky/godowsky_v2_chopin_op25_e05.mid', 
	'Godowsky/godowsky_v2_chopin_op25_e09.mid', 
	'Godowsky/godowsky_v3_chopin_op10_e07.mid', 
	'Godowsky/godowsky_v3_chopin_op10_e09.mid', 
	'Godowsky/godowsky_v3_chopin_op25_e01.mid', 
	'Godowsky/godowsky_v3_chopin_op25_e02.mid', 
	'Godowsky/godowsky_v3_chopin_op25_e05.mid', 
	'Godowsky/godowsky_v4_chopin_op25_e02.mid', 
	'Godowsky/godowsky_v5_chopin_op10_e05.mid', 
	'Godowsky/godowsky_v6_chopin_op10_e05.mid', 
	'Godowsky/godowsky_v7_chopin_op10_e05.mid'
]

for piece in LIST_TO_PROCESS:
	preprocessFile(PATH_TO_DATASET + piece, PATH_TO_PROCESSED_FILES + piece)

preprocessFile('Godowtsai Dataset/Chopin/chopin_op10_e01.mid', 'Output Midi/chopin_op10_e01_proc.mid')
preprocessFile('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e01.mid', 'Output Midi/godowsky_v1_chopin_op10_e01_proc.mid')

# (57-6*0.0625)/41
timeScale = 1.395

scalePiece('Output Midi/godowsky_v1_chopin_op10_e01_proc.mid', 'Output Midi/godowsky_v1_chopin_op10_e01_scaled.mid', timeScale, -12)

# (38+9*0.0625)/(46+1.5*0.0625)
timeScale = 0.8366101695

preprocessFile('Godowtsai Dataset/Chopin/chopin_op10_e02.mid', 'Output Midi/chopin_op10_e02_proc.mid')
preprocessFile('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e02.mid', 'Output Midi/godowsky_v1_chopin_op10_e02_proc.mid')

scalePiece('Output Midi/godowsky_v1_chopin_op10_e02_proc.mid', 'Output Midi/godowsky_v1_chopin_op10_e02_scaled.mid', timeScale, 0)

# onlyNote('Godowtsai Dataset/Chopin/chopin_op10_e01.mid', 'Output Midi/chopin_op10_e01_no_tempo.mid', 357)
# printMidi('Output Midi/chopin_op10_e01_no_tempo.mid')
# onlyNote('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e01.mid', 'Output Midi/godowsky_v1_chopin_op10_e01_no_tempo.mid', -1)

# shiftAndScale('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e01.mid', 'Output Midi/godowsky_v1_chopin_op10_e01_shifted.mid', -12, 0.33) #0.3449)


# printMidi('Godowtsai Dataset/Chopin/chopin_op10_e02.mid')
# onlyNote('Godowtsai Dataset/Chopin/chopin_op10_e02.mid', 'Output Midi/chopin_op10_e02_no_tempo.mid', 0)
# printMidi('Output Midi/chopin_op10_e01_no_tempo.mid')
# onlyNote('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e02.mid', 'Output Midi/godowsky_v1_chopin_op10_e02_no_tempo.mid', -1)

# shiftAndScale('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e02.mid', 'Output Midi/godowsky_v1_chopin_op10_e02_shifted.mid', -12, 0.33) #0.3449)
