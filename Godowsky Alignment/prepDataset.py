# import mido
# import random
import pretty_midi
import numpy as np
import csv

# from mido import Message, MidiFile, MidiTrack
from midi2audio import FluidSynth

import matplotlib.pyplot as plt


def printMidi(fileName):
    '''
    Input: path to a MIDI file

    Prints out every message in the MIDI file
    '''
    midiToPlay = MidiFile(fileName)
    for track in midiToPlay.tracks:
        for msg in track:
            print(msg)

def cutInitialSilence(inputFileName, outputFileName):
    '''
    Input: path to a MIDI file to remove silence from, path to a file to save
    the modified MIDI file

    Takes in a MIDI file with specified file path, and returns a new MIDI file
    with the silence at the beginning removed.
    '''

    # Load MIDI file into PrettyMIDI object
    midi_data = pretty_midi.PrettyMIDI(inputFileName)

    # Make a new PrettyMIDI object for the modified file
    modified_data = midi_data

    first_onset = 10000

    for instrument in midi_data.instruments:
        if instrument.get_onsets()[0] < first_onset:
            first_onset = instrument.get_onsets()[0]

    if first_onset > 0:
        for instrument in modified_data.instruments:
            for note in instrument.notes:
                note.start = note.start - first_onset
                note.end = note.end - first_onset

    modified_data.write(outputFileName)


def createTimeAlignment(songOnePath, songTwoPath, outputSongPath, outputFileName, songOneMeasures, songTwoMeasures, alignByMeasure):
    '''
    Inputs: paths to 2 MIDI files, a path to a file to write the modified version of songOne to, and a path to
     a list of which measures correspond in the piece, and a boolean that specifies whether to align by measure
     (as opposed to aligning every beat)

    Expected format of the measures is:
        songOneMeasures=[(1, 45), (60,75)]
        songTwoMeasures=[(1,45), (62,77)]
    Takes in a boolean alignByMeasure
        If true, only aligns the first beat in each measure
        If false, aligns every beat in each measure
    '''

    # get the midi data
    midiDataOne = pretty_midi.PrettyMIDI(songOnePath)
    midiDataTwo = pretty_midi.PrettyMIDI(songTwoPath)
    # find each time signature
    timeSigOne = 2 #midiDataOne.time_signature_changes[0].numerator
    timeSigTwo = 2 #midiDataTwo.time_signature_changes[0].numerator
    # timeSigTwo = 2
    # build up the beat arrays
    beatsOne = np.array([], dtype='int')
    beatsTwo = np.array([], dtype='int')

    print("1: " + str(len(midiDataOne.get_beats())))
    print("2: " + str(len(midiDataTwo.get_beats())))
    print(midiDataOne.get_beats())
    print(midiDataTwo.get_beats())

    print("end 1: " + str(midiDataOne.get_end_time()))
    print("end 2: " + str(midiDataTwo.get_end_time()))

    # for each song, go through each section that should line up
    for tup in songOneMeasures:
        startMeasure = tup[0]
        endMeasure = tup[1]
        startBeat = (startMeasure - 1) * timeSigOne
        endBeat = (endMeasure - 1) * timeSigOne + 1
        if alignByMeasure:
            newBeats = range(startBeat, endBeat + 1, timeSigOne)
        else:
            newBeats = range(startBeat, endBeat + 1, 1)
        # add on your new beats
        beatsOne = np.append(beatsOne, newBeats)

    for tup in songTwoMeasures:
        startMeasure = tup[0]
        endMeasure = tup[1]
        startBeat = (startMeasure - 1) * timeSigTwo
        endBeat = (endMeasure - 1) * timeSigTwo + 1
        if alignByMeasure:
            newBeats = range(startBeat, endBeat + 1, timeSigTwo)
        else:
            newBeats = range(startBeat, endBeat + 1, 1)
        # add on the new beats
        beatsTwo = np.append(beatsTwo, newBeats)

    # TODO: Should we always align the last beat?

    print(beatsOne)
    print(beatsTwo)

    timesOne, timesTwo = createTimeAlignmentFromBeats(songOnePath, songTwoPath, beatsOne, beatsTwo, outputSongPath, outputFileName)

    return (timesOne, timesTwo)

def createTimeAlignmentFromBeats(songOnePath, songTwoPath, songOneAlignedBeats, songTwoAlignedBeats, outputSongPath, outputFileName):
    '''
    Inputs: paths to 2 MIDI files, 2 lists of beats that align, an output path to save a modified MIDI file to, and the outputFileName
    to write the csv file to

    Creates an aligned midi file by scaling the beats as specified, and applies these scalings to songOne.
    The modified songOne and original songTwo should be aligned when played together.
    '''

    midiDataOne = pretty_midi.PrettyMIDI(songOnePath)
    midiDataTwo = pretty_midi.PrettyMIDI(songTwoPath)

    songOneBeats = midiDataOne.get_beats()
    songTwoBeats = midiDataTwo.get_beats()

    numBeats = len(songOneAlignedBeats)

    print(numBeats)

    timesOne = np.empty(numBeats)
    timesTwo = np.empty(numBeats)

    for i in range(numBeats):
        timesOne[i] = songOneBeats[songOneAlignedBeats[i]]
        timesTwo[i] = songTwoBeats[songTwoAlignedBeats[i]]

    modified = midiDataOne
    modified.adjust_times(timesOne, timesTwo)
    modified.write(outputSongPath)
    formatTimeAlignment(timesOne, timesTwo, outputFileName)

    return (timesOne, timesTwo)

def formatTimeAlignment(timesOne, timesTwo, outputFileName):
    with open(outputFileName, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for i in range (len(timesOne)):
            filewriter.writerow([str(timesOne[i]), str(timesTwo[i])])


# cutInitialSilence('Godowtsai Dataset/Chopin/chopin_op10_3.mid', 'chopin_op10_03_again_edited.mid')
# createTimeAlignment('chopin_op10_03_again_edited.mid', 'godowsky_v1_chopin_op10_e03_edited.mid', 'chopin_op10_e03_aligned.mid', 'alignment_chopin_op10_e03.csv', [(1, 45), (62,77)], [(1,45), (60,75)], False)

cutInitialSilence('Godowtsai Dataset/Chopin/chopin_op10_e01.mid', 'chopin_op10_e01_edited.mid')
cutInitialSilence('Godowtsai Dataset/Godowsky/godowsky_v1_chopin_op10_e01.mid', 'godowsky_v1_chopin_op10_e01_edited.mid')

createTimeAlignment('chopin_op10_e01_edited.mid', 'godowsky_v1_chopin_op10_e01_edited.mid', 'chopin_op10_e01_aligned.mid', 'Godowtsai Dataset/Ground Truth Alignments/alignment_chopin_op10_e01.csv', [(1, 80)], [(1,80)], True)




'''
Take in MIDI file and will shift the piece by specified pitchShift
(positive pitchShift shifts piece up, negative pitchShift shifts the
piece down by specified number of notes)
'''
def pitchShiftPiece(inputFileName, outputFileName, pitchShift):
    # Load MIDI file into PrettyMIDI object
    midi_data = pretty_midi.PrettyMIDI(inputFileName)

    for instrument in midi_data.instruments:
        for note in instrument.notes:
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
# name='godowsky_v1_chopin_op10_e03.mid'
# scalePiece(PATH_TO_PROCESSED_FILES + name, PATH_TO_SCALED_FILES + name, 0.9544534413, 3)

# name='godowsky_v1_chopin_op10_e05.mid'
# scalePiece(PATH_TO_PROCESSED_FILES + name, PATH_TO_SCALED_FILES + name, 1.0259179266, 0)

# fs = FluidSynth()
# fs.midi_to_audio(PATH_TO_SCALED_FILES + name, PATH_TO_WAV_FILES + name[:-4] + '.wav')









# def onlyNote(inputFileName, outputFileName, shiftFront):
#   orig = MidiFile(inputFileName)
#   mid = MidiFile()

#   for tr in orig.tracks:
#       track = MidiTrack()
#       mid.tracks.append(track)
#       #<meta message track_name name='Grand Piano' time=0>

#       # msg = Message('note_on', note=0, velocity=0, time=timeShift)
#       # track.append(msg)

#       for msg in tr:
#           if msg.type == 'note_on' or msg.type == 'note_off':
#               if msg.time != shiftFront:
#                   track.append(msg)
#   mid.save(outputFileName)

# def shiftAndScale(inputFileName, outputFileName, pitchShift, timeScale):
#   orig = MidiFile(inputFileName)
#   mid = MidiFile()

#   for tr in orig.tracks:
#       track = MidiTrack()
#       mid.tracks.append(track)
# #<meta message track_name name='Grand Piano' time=0>
        
#       # time=0 could be replaced be time=timeShift if necessary
#       msg = Message('note_on', note=0, velocity=0, time=0)
#       track.append(msg)

#       for msg in tr:
#           if msg.type == 'note_on':
#               msg.time = round(msg.time * timeScale)
#               msg.note = msg.note + pitchShift
#               track.append(msg)
#   mid.save(outputFileName)


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
