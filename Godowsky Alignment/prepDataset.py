# import mido
# import random
import pretty_midi

# from mido import Message, MidiFile, MidiTrack
from midi2audio import FluidSynth

def printMidi(fileName):
	midiToPlay = MidiFile(fileName)
	for track in midiToPlay.tracks:
	    for msg in track:
	        print(msg)

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

	modified_data.fluidsynth
	modified_data.write(outputFileName)

'''
Take in processed file (one track, no initial silence), and
scale by the time provided (timeScale > 1 will stretch the piece,
timeScale < 1 will compress the piece) and will shift the piece
by specified pitchShift (positive pitchShift shifts piece up,
negative pitchShift shifts the piece down by specified number of
notes)
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
PATH_TO_PROCESSED_FILES = 'Output/Processed/'
PATH_TO_SCALED_FILES = 'Output/Scaled/'
PATH_TO_WAV_FILES = 'Output/Wav/'

CHOPIN_LIST = [
	'chopin_op10_e01.mid',
	'chopin_op10_e02.mid',
	'chopin_op10_e03.mid',
	'chopin_op10_e04.mid',
	'chopin_op10_e05.mid',
	'chopin_op10_e06.mid',
	'chopin_op10_e07.mid',
	'chopin_op10_e08.mid',
	'chopin_op10_e09.mid',
	'chopin_op10_e10.mid',
	'chopin_op10_e11.mid',
	'chopin_op10_e12.mid',
	'chopin_op25_e01.mid',
	'chopin_op25_e02.mid',
	'chopin_op25_e03.mid',
	'chopin_op25_e04.mid',
	'chopin_op25_e05.mid',
	'chopin_op25_e06.mid',
	'chopin_op25_e07.mid',
	'chopin_op25_e08.mid',
	'chopin_op25_e09.mid',
	'chopin_op25_e10.mid',
	'chopin_op25_e11.mid',
	'chopin_op25_e12.mid'
]

GODOWSKY_LIST = [
	('godowsky_v1_chopin_op10_e01.mid', 1.395, -12),
	('godowsky_v1_chopin_op10_e02.mid', 0.8366101695, 0),
	('godowsky_v1_chopin_op10_e03.mid', 1, 0),
	('godowsky_v1_chopin_op10_e04.mid', 1, 0),
	('godowsky_v1_chopin_op10_e05.mid', 1, 0),
	('godowsky_v1_chopin_op10_e06.mid', 1, 0),
	('godowsky_v1_chopin_op10_e07.mid', 1, 0),
	('godowsky_v1_chopin_op10_e08.mid', 1, 0),
	('godowsky_v1_chopin_op10_e09.mid', 1, 0),
	('godowsky_v1_chopin_op10_e10.mid', 1, 0),
	('godowsky_v1_chopin_op10_e11.mid', 1, 0),
	('godowsky_v1_chopin_op10_e12.mid', 1, 0),
	('godowsky_v1_chopin_op25_e01.mid', 1, 0),
	('godowsky_v1_chopin_op25_e02.mid', 1, 0),
	('godowsky_v1_chopin_op25_e03.mid', 1, 0),
	('godowsky_v1_chopin_op25_e04.mid', 1, 0),
	('godowsky_v1_chopin_op25_e05.mid', 1, 0),
	('godowsky_v1_chopin_op25_e06.mid', 1, 0),
	('godowsky_v1_chopin_op25_e08.mid', 1, 0),
	('godowsky_v1_chopin_op25_e09.mid', 1, 0),
	('godowsky_v1_chopin_op25_e10.mid', 1, 0),
	('godowsky_v1_chopin_op25_e11.mid', 1, 0),
	('godowsky_v1_chopin_op25_e12.mid', 1, 0),
	('godowsky_v2_chopin_op10_e01.mid', 1, 0),
	('godowsky_v2_chopin_op10_e02.mid', 1, 0),
	('godowsky_v2_chopin_op10_e05.mid', 1, 0),
	('godowsky_v2_chopin_op10_e07.mid', 1, 0),
	('godowsky_v2_chopin_op10_e08.mid', 1, 0),
	('godowsky_v2_chopin_op10_e09.mid', 1, 0),
	('godowsky_v2_chopin_op10_e10.mid', 1, 0),
	('godowsky_v2_chopin_op25_e01.mid', 1, 0),
	('godowsky_v2_chopin_op25_e02.mid', 1, 0),
	('godowsky_v2_chopin_op25_e03.mid', 1, 0),
	('godowsky_v2_chopin_op25_e04.mid', 1, 0),
	('godowsky_v2_chopin_op25_e05.mid', 1, 0),
	('godowsky_v2_chopin_op25_e09.mid', 1, 0),
	('godowsky_v3_chopin_op10_e07.mid', 1, 0),
	('godowsky_v3_chopin_op10_e09.mid', 1, 0),
	('godowsky_v3_chopin_op25_e01.mid', 1, 0),
	('godowsky_v3_chopin_op25_e02.mid', 1, 0),
	('godowsky_v3_chopin_op25_e05.mid', 1, 0),
	('godowsky_v4_chopin_op25_e02.mid', 1, 0),
	('godowsky_v5_chopin_op10_e05.mid', 1, 0),
	('godowsky_v6_chopin_op10_e05.mid', 1, 0),
	('godowsky_v7_chopin_op10_e05.mid', 1, 0)
]

def preprocessAllFiles():
	for piece in CHOPIN_LIST:
		preprocessFile(PATH_TO_DATASET + 'Chopin/' + piece, PATH_TO_PROCESSED_FILES + piece)
	for piece in GODOWSKY_LIST:
		preprocessFile(PATH_TO_DATASET + 'Godowsky/' + piece[0], PATH_TO_PROCESSED_FILES + piece[0])

def scaleGodowskyFiles():
	for piece in GODOWSKY_LIST:
		scalePiece(PATH_TO_PROCESSED_FILES + piece[0], PATH_TO_SCALED_FILES + piece[0], piece[1], piece[2])

def convertFilesToWav():
	fs = FluidSynth()

	for piece in CHOPIN_LIST:
		fs.midi_to_audio(PATH_TO_PROCESSED_FILES + piece, PATH_TO_WAV_FILES + piece[:-4] + '.wav')
	for piece in GODOWSKY_LIST:
		fs.midi_to_audio(PATH_TO_SCALED_FILES + piece[0], PATH_TO_WAV_FILES + piece[0][:-4] + '.wav')

# preprocessAllFiles()
# scaleGodowskyFiles()
# convertFilesToWav()


# To align a single Godowsky file:
name='godowsky_v1_chopin_op10_e03.mid'
scalePiece(PATH_TO_PROCESSED_FILES + name, PATH_TO_SCALED_FILES + name, 0.9544534413, 3)

name='godowsky_v1_chopin_op10_e05.mid'
scalePiece(PATH_TO_PROCESSED_FILES + name, PATH_TO_SCALED_FILES + name, 1.0259179266, 0)

fs = FluidSynth()
fs.midi_to_audio(PATH_TO_SCALED_FILES + name, PATH_TO_WAV_FILES + name[:-4] + '.wav')

# def onlyNote(inputFileName, outputFileName, shiftFront):
# 	orig = MidiFile(inputFileName)
# 	mid = MidiFile()

# 	for tr in orig.tracks:
# 		track = MidiTrack()
# 		mid.tracks.append(track)
# 		#<meta message track_name name='Grand Piano' time=0>

# 		# msg = Message('note_on', note=0, velocity=0, time=timeShift)
# 		# track.append(msg)

# 		for msg in tr:
# 			if msg.type == 'note_on' or msg.type == 'note_off':
# 				if msg.time != shiftFront:
# 					track.append(msg)
# 	mid.save(outputFileName)

# def shiftAndScale(inputFileName, outputFileName, pitchShift, timeScale):
# 	orig = MidiFile(inputFileName)
# 	mid = MidiFile()

# 	for tr in orig.tracks:
# 		track = MidiTrack()
# 		mid.tracks.append(track)
# #<meta message track_name name='Grand Piano' time=0>
		
# 		# time=0 could be replaced be time=timeShift if necessary
# 		msg = Message('note_on', note=0, velocity=0, time=0)
# 		track.append(msg)

# 		for msg in tr:
# 			if msg.type == 'note_on':
# 				msg.time = round(msg.time * timeScale)
# 				msg.note = msg.note + pitchShift
# 				track.append(msg)
# 	mid.save(outputFileName)


# # (57-6*0.0625)/41
# timeScale = 1.395

# scalePiece('Output/godowsky_v1_chopin_op10_e01_proc.mid', 'Output/godowsky_v1_chopin_op10_e01_scaled.mid', timeScale, -12)

# # (38+9*0.0625)/(46+1.5*0.0625)
# timeScale = 0.8366101695

# preprocessFile('Godowtsai Dataset/chopin_op10_e02.mid', 'Output/chopin_op10_e02_proc.mid')
# preprocessFile('Godowtsai Dataset/godowsky_v1_chopin_op10_e02.mid', 'Output/godowsky_v1_chopin_op10_e02_proc.mid')

# scalePiece('Output/godowsky_v1_chopin_op10_e02_proc.mid', 'Output/godowsky_v1_chopin_op10_e02_scaled.mid', timeScale, 0)

# onlyNote('Godowtsai Dataset/chopin_op10_e01.mid', 'Output/chopin_op10_e01_no_tempo.mid', 357)
# printMidi('Output/chopin_op10_e01_no_tempo.mid')
# onlyNote('Godowtsai Dataset/godowsky_v1_chopin_op10_e01.mid', 'Output/godowsky_v1_chopin_op10_e01_no_tempo.mid', -1)

# shiftAndScale('Godowtsai Dataset/godowsky_v1_chopin_op10_e01.mid', 'Output/godowsky_v1_chopin_op10_e01_shifted.mid', -12, 0.33) #0.3449)


# printMidi('Godowtsai Dataset/chopin_op10_e02.mid')
# onlyNote('Godowtsai Dataset/chopin_op10_e02.mid', 'Output/chopin_op10_e02_no_tempo.mid', 0)
# printMidi('Output/chopin_op10_e01_no_tempo.mid')
# onlyNote('Godowtsai Dataset/godowsky_v1_chopin_op10_e02.mid', 'Output/godowsky_v1_chopin_op10_e02_no_tempo.mid', -1)

# shiftAndScale('Godowtsai Dataset/godowsky_v1_chopin_op10_e02.mid', 'Output/godowsky_v1_chopin_op10_e02_shifted.mid', -12, 0.33) #0.3449)
