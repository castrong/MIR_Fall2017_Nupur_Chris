from mido import Message, MidiFile, MidiTrack
from PIL import Image

import os
import csv
import numpy as np
import nltk
import random
import mido

def midiToCSV(directoriesIn, directoryOut):

    directories = directoriesIn
    totalFiles = 0

    for directoryIndex in range(len(directories)):
        directory = directories[directoryIndex]
        print('==> Analyzing directory %s'%(directory))
        
        # grab the files, assume they're all midi
        files = os.listdir(directory)
        for i in range(len(files)):
            if '.DS_Store' not in files[i] and '._' not in files[i]:
                totalFiles = totalFiles + 1
                print('Processing file %g out of %g in directory: %s'%(i, len(files), files[i]))
                mid = MidiFile(directory + files[i])

                noteonList = []
                midimsgList = []
                accTime = []
                countNote = 0
                startTime = 0
                
                for msg in mid:

                    # add all messages to list for ease of access
                    midimsgList.append(msg)

                    # Iterate through all midi message and accumulate time stamps
                    if accTime == []:
                        accTime.append(startTime)
                    else:
                        accTime.append(msg.time + accTime[-1])

                for j in range(len(midimsgList)):
                    msg = midimsgList[j]

                    if msg.type == 'note_on' and msg.velocity > 0:
                        countNote = countNote + 1 # for verification

                        # loop through the message after the j-th message to find corresponding note-off event
                        for k in range(j+1, len(midimsgList)):
                            nextmsg = midimsgList[k]

                            # Note: some midi files have no note-off events. Instead, it is note-on event with velocity = 0
                            if nextmsg.type == 'note_off' or (nextmsg.type == 'note_on' and nextmsg.velocity == 0):
                                if nextmsg.note == msg.note:
                                    noteonList.append([msg.note, accTime[j], msg.velocity, accTime[k]-accTime[j]])
                                    break

                # Check that every note onset gets released
                if countNote != len(noteonList):
                    print("Mismatched number of data points. Something is wrong!", countNote, len(noteonList))
                else:
                    # Save list of note onsets to csv file
                    name = files[i].split('.')
                    outFileName = directoryOut +name[0]+'_'+directory[:-1]+'.csv'
                    with open(outFileName, 'w') as csvfile:
                        spamwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        for row in noteonList:
                            spamwriter.writerow(row)


def createMatrixFromCSV(filepath, onsetOnly, timePerChunk=0.1):
	'''
	Take a CSV file where row represents a note onset (note, onset_time, velocity, duration)
	and convert it into a matrix of size num_notes (128) x timeChunks x 2. The first element in the third
	dimension will be duration and the second will be velocity

	If onsetOnly is true, the duration and velocity will only appear in the time chunk of onset
	If onsetOnly is false, the duration and velocity will appear in any time chunks the note is held during

	Inputs
	filepath: Filepath of the CSV file
	onsetOnly: whether to fill the matrix only at onset, or throughout its duration
	timePerChunk: how much time each column in the matrix represents

	Output:
	a num_notes x timeChunks x 2 (duration and velocity) matrix. 
	'''
	numPitches = 128;

	# open your csv file
	with open(filepath, 'r') as csvfile:
		print("==> Reading File: %s"%(filepath))
		myReader = csv.reader(csvfile)
		# find the max time to figure out how big your matrix should be
		maxTime = max([float(row[1]) for row in myReader])
		# reset the reader
		csvfile.seek(0)

		# open it again to actually parse it, now that you know how big your matrix should be
		curMatrix = np.zeros((numPitches, int(np.ceil(maxTime / timePerChunk)), 2))
		
		# read each row and add into the matrix that represents the song
		# the csv is in the form: note, time, velocity, duration and has a row for every note onset in the song
		numNotes = 0
		for row in myReader:
			numNotes = numNotes + 1
			[note, curTime, velocity, duration] = [int(row[0]), float(row[1]), int(row[2]), float(row[3])]
			
			# either put an entry just for the onset, or put an entry at every point in its duration
			if onsetOnly:
				curMatrix[note, int(np.floor(curTime / timePerChunk)), :] = [duration, velocity]
			else :
				# fill in spots after the onset based on the duration
				# any spot in the matrix it is on during gets turned on
				curMatrix[note, int(np.floor(curTime / timePerChunk)):int(np.floor((curTime + duration) / timePerChunk)) + 1, :] = [duration, velocity]

	return curMatrix

'''
Takes in boolean array, returns a row vector containing the index of the lowest
column containing a value of "True". If there are no True values in the column, the
value is 0.

Test:
testMat = np.array([[ True, False, False,  True],
	   [False, False,  True, False],
	   [False,  True, False, False]])

print(testMat)

print(oneDimArray(testMat))
'''
def generateOneDimArray(logicalMat):
	arr = np.zeros(logicalMat.shape[1])

	for col in range(logicalMat.shape[1]):
		for row in range(logicalMat.shape[0]):
			if logicalMat[row][col]:
				arr[col] = row
	return arr

def stripZeros(oneDimArr):
	return np.array([x for x in oneDimArr if x != 0])

def ngrams(n, words):
	gram = dict()
	# Populate 3-gram dictionary
	for i in range(len(words)-(n-1)):
		if n == 2:
			key = (words[i], words[i+1])
		elif n == 3:
			key = (words[i], words[i+1], words[i+2])
		elif n == 4:
			key = (words[i], words[i+1], words[i+2], words[i+3])
		elif n == 5:
			key = (words[i], words[i+1], words[i+2], words[i+3], words[i+4])
		elif n == 6:
			key = (words[i], words[i+1], words[i+2], words[i+3], words[i+4], words[i+5])
		elif n == 7:
			key = (words[i], words[i+1], words[i+2], words[i+3], words[i+4], words[i+5], words[i+6])
		elif n == 8:
			key = (words[i], words[i+1], words[i+2], words[i+3], words[i+4], words[i+5], words[i+6], words[i+7])
		else:
			print("Sorry, can't support more than 8-gram")
		
		if key in gram:
			gram[key] += 1
		else:
			gram[key] = 1

	# Turn into a list of (word, count) sorted by count from most to least
	gram = sorted(gram.items(), key=lambda words: words[1], reverse = True)
	return gram
	
def getNGramSongRandom(n, words, seqLength, gram):
	song = []

	if n >= 3:
		song.append(words[0])
	if n >= 4:
		song.append(words[1])
	if n >= 5:
		song.append(words[2])
	if n >= 6:
		song.append(words[3])
	if n >= 7:
		song.append(words[4])
	if n >= 8:
		song.append(words[5])

	for i in range(seqLength):
		song.append(words[n-2])
		# Get all possible elements ((first word, second word, ...), frequency)
		if n == 2:
			choices = [element for element in gram if element[0][0] == words[0]]
		elif n == 3:
			choices = [element for element in gram if element[0][0] == words[0] and element[0][1] == words[1]]
		elif n == 4:
			choices = [element for element in gram if element[0][0] == words[0] and element[0][1] == words[1] and element[0][2] == words[2]]
		elif n == 5:
			choices = [element for element in gram if element[0][0] == words[0] and element[0][1] == words[1] and element[0][2] == words[2] and element[0][3] == words[3]]
		elif n == 6:
			choices = [element for element in gram if element[0][0] == words[0] and element[0][1] == words[1] and element[0][2] == words[2] and element[0][3] == words[3] and element[0][4] == words[4]]
		elif n == 7:
			choices = [element for element in gram if element[0][0] == words[0] and element[0][1] == words[1] and element[0][2] == words[2] and element[0][3] == words[3] and element[0][4] == words[4] and element[0][5] == words[5]]
		elif n == 8:
			choices = [element for element in gram if element[0][0] == words[0] and element[0][1] == words[1] and element[0][2] == words[2] and element[0][3] == words[3] and element[0][4] == words[4] and element[0][5] == words[5] and element[0][6] == words[6]]
		else:
			print("Sorry, can't support more than 8-gram")

		if not choices:
			break
		
		# Choose a pair with weighted probability from the choice list
		if n >= 2:
			words[0] = weighted_choice(choices)[1]
		if n >= 3:
			words[1] = weighted_choice(choices)[2]
		if n >= 4:
			words[2] = weighted_choice(choices)[3]
		if n >= 5:
			words[3] = weighted_choice(choices)[4]
		if n >= 6:
			words[4] = weighted_choice(choices)[5]
		if n >= 7:
			words[5] = weighted_choice(choices)[6]
		if n >= 8:
			words[6] = weighted_choice(choices)[7]
	return song

def weighted_choice(choices):
	total = sum(w for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for c, w in choices:
		if upto + w > r:
			return c
		upto += w

def oneDimArrayToMidi(oneDimArr, name):
	#orig = MidiFile('Midi/rh.mid')

	mid = MidiFile()
	track = MidiTrack()
	mid.tracks.append(track)

	# for tr in orig.tracks:
	# 	for msg in tr:
	# 		msg_count = msg_count + 1
	# 		if msg.type == 'note_on':
	# 			if (counter < len(oneDimArr)):
	# 				msg.note = int(oneDimArr[counter])
	# 			else:
	# 				msg.note = 0
	# 			track.append(msg)
	# 			counter = counter + 1

	for i in range(len(oneDimArr)):
		if (oneDimArr[i] > 0.0 and oneDimArr[i] < 127.0):
			msg1 = mido.Message('note_on', note=int(oneDimArr[i]), velocity=60, time=0)
			msg2 = mido.Message('note_on', note=int(oneDimArr[i]), velocity=0, time=80)
			track.append(msg1)
			track.append(msg2)

	mid.save(name)

def dealWithWeirdMidi():
	orig = MidiFile('Midi/original_rh.mid')
	rh = MidiFile()
	rh.tracks.append(orig.tracks[3])
	rh.save('Midi/rh.mid')

def generateTransitionMatrix(bigramList):
	'''
	Generate a transition matrix from a bigram list
	The i, jth location in the matrix represents the frequency of the ith note being
	followed by the jth note.

	The function will return a dictionary of notes --> columns, so that you know which 
	absolute note is the ith / jth note (maps note number to column in the array)

	The function returns both the transition matrix, and the dictionary of notes to columns
	'''

	# Initialize Variables
	noteToColumnDict = {}
	numNotesSeen = 0
	transitionMatrix = np.empty((0,0))

	# Loop through each bigram + frequency tuple
	for bigramTuple in bigramList:
		# accumulate a matrix of the occurence of each note after each other note
		# grab the information from your current bigram tuple, which has the bigram and its frequency
		(noteOne, noteTwo) = bigramTuple[0]
		freq = bigramTuple[1]

		# if you haven't seen the note before give it a row and column in the matrix
		if noteOne not in noteToColumnDict:
			noteToColumnDict[noteOne] = numNotesSeen
			numNotesSeen = numNotesSeen + 1
			transitionMatrix = np.lib.pad(transitionMatrix, (0,1), 'constant', constant_values=(1,0))
		if noteTwo not in noteToColumnDict:
			noteToColumnDict[noteTwo] = numNotesSeen
			numNotesSeen = numNotesSeen + 1
			transitionMatrix = np.lib.pad(transitionMatrix, (0,1), 'constant', constant_values=(1,0))

		# set the current spot in the transition matrix to the observed frequency
		transitionMatrix[noteToColumnDict[noteTwo], noteToColumnDict[noteOne]] = freq

	# normalize the matrix so that each column sums to 1 (each represents frequency instead of absolute amounts)
	transitionMatrix = transitionMatrix / np.sum(transitionMatrix, 0)
	return transitionMatrix, noteToColumnDict


def getSteadyStateDistribution(matrix, initialCondition):
	largeNum = 2000
	return np.linalg.matrix_power(matrix, largeNum).dot(initialCondition)


def colToNote(col, noteToColumnDict):
	keys = [key for key, value in noteToColumnDict.items() if value == col]
	# should just be one element
	return keys[0]

def generateSequenceFromTransitionMatrix(transitionMatrix, noteToColumnDict, initialCondition, seqLength):
	seq = []
	numNotes = transitionMatrix.shape[0] # equal to the number of rows or columns
	curDistribution = initialCondition

	# create samples for your sequence by randomly picking out of your current distribution
	# then updating the distribution with the transition matrix
	for i in range(seqLength):
		# sample the column number, then convert it to a note
		choice = np.random.choice(range(numNotes), p=curDistribution)
		seq = seq + [colToNote(choice, noteToColumnDict)]
		# update distribution
		curDistribution = transitionMatrix.dot(curDistribution)

	# map from column numbers back to notes
	return seq

def generateIntervalArray(oneDimArr):
	intervalArr = np.zeros(oneDimArr.shape[0] - 1)

	for i in range(1, oneDimArr.shape[0]):
		intervalArr[i-1] = oneDimArr[i] - oneDimArr[i-1]

	return intervalArr

def intervalArrayToNoteArray(intervalArr, startNote):
	noteArr = [0] * (len(intervalArr) + 1)
	noteArr[0] = startNote

	for i in range(1, len(intervalArr) + 1):
		noteArr[i] = noteArr[i-1] + intervalArr[i-1]

	return noteArr


#midiToCSV(['Midi/'], 'CSV_From_Midi/')
#dealWithWeirdMidi()

origMatrix = createMatrixFromCSV('CSV_From_Midi/rh_Midi.csv', True)
origVelocityOnly = origMatrix[:,:, 1] # pick out just the velocity
origLogicalMat = origVelocityOnly.astype(bool)
origOneDimWithZeros = generateOneDimArray(origLogicalMat)
origOneDim = stripZeros(origOneDimWithZeros)
lengthOfSong = origOneDim.shape[0]

#print(origOneDim)

# Note n grams

gram2 = ngrams(2, origOneDim)
song2gram = getNGramSongRandom(2, [70.0], lengthOfSong, gram2)
oneDimArrayToMidi(song2gram, 'Midi/bigram.mid')

gram3 = ngrams(3, origOneDim)
song3gram = getNGramSongRandom(3, [70.0, 61.0], lengthOfSong, gram3)
oneDimArrayToMidi(song3gram, 'Midi/trigram.mid')

gram4 = ngrams(4, origOneDim)
song4gram = getNGramSongRandom(4, [70.0, 61.0, 66.0], lengthOfSong, gram4)
oneDimArrayToMidi(song4gram, 'Midi/4gram.mid')

gram5 = ngrams(5, origOneDim)
song5gram = getNGramSongRandom(5, [70.0, 61.0, 66.0, 63.0], lengthOfSong, gram5)
oneDimArrayToMidi(song5gram, 'Midi/5gram.mid')

gram6 = ngrams(6, origOneDim)
song6gram = getNGramSongRandom(6, [70.0, 61.0, 66.0, 63.0, 66.0], lengthOfSong, gram6)
oneDimArrayToMidi(song6gram, 'Midi/6gram.mid')

gram7 = ngrams(7, origOneDim)
song7gram = getNGramSongRandom(7, [70.0, 61.0, 66.0, 63.0, 66.0, 66.0], lengthOfSong, gram7)
oneDimArrayToMidi(song7gram, 'Midi/7gram.mid')

gram8 = ngrams(8, origOneDim)
song8gram = getNGramSongRandom(8, [70.0, 61.0, 66.0, 63.0, 66.0, 66.0, 58.0], lengthOfSong, gram8)
oneDimArrayToMidi(song8gram, 'Midi/8gram.mid')

# test
bigramList = ngrams(2, origOneDim)
matrix, noteToCol = generateTransitionMatrix(bigramList)

initialCond = np.zeros(matrix.shape[0])
initialCond[noteToCol[70]] = 1
steadyState = getSteadyStateDistribution(matrix, initialCond)

seq = generateSequenceFromTransitionMatrix(matrix, noteToCol, initialCond, lengthOfSong)
oneDimArrayToMidi(seq, 'Midi/transition.mid')

# Interval n grams

intervalOrig = generateIntervalArray(origOneDim)
print(intervalOrig)

gram2 = ngrams(2, intervalOrig)
int2gram = getNGramSongRandom(2, [-9, 5], lengthOfSong, gram2)
song2gram = intervalArrayToNoteArray(int2gram, 70.0)
oneDimArrayToMidi(song2gram, 'Midi/bigram_int.mid')

gram3 = ngrams(3, intervalOrig)
int3gram = getNGramSongRandom(3, [-9, 5, -3], lengthOfSong, gram3)
song3gram = intervalArrayToNoteArray(int3gram, 70.0)
oneDimArrayToMidi(song2gram, 'Midi/trigram_int.mid')

gram4 = ngrams(4, intervalOrig)
int4gram = getNGramSongRandom(4, [-9, 5, -3, 3], lengthOfSong, gram4)
song4gram = intervalArrayToNoteArray(int4gram, 70.0)
oneDimArrayToMidi(song4gram, 'Midi/4gram_int.mid')

gram5 = ngrams(5, intervalOrig)
int5gram = getNGramSongRandom(5, [-9, 5, -3, 3, 0], lengthOfSong, gram5)
song5gram = intervalArrayToNoteArray(int5gram, 70.0)
oneDimArrayToMidi(song5gram, 'Midi/5gram_int.mid')

gram6 = ngrams(6, intervalOrig)
int6gram = getNGramSongRandom(6, [-9, 5, -3, 3, 0, -8], lengthOfSong, gram6)
song6gram = intervalArrayToNoteArray(int6gram, 70.0)
oneDimArrayToMidi(song6gram, 'Midi/6gram_int.mid')

gram7 = ngrams(7, intervalOrig)
int7gram = getNGramSongRandom(7, [-9, 5, -3, 3, 0, -8, 3], lengthOfSong, gram7)
song7gram = intervalArrayToNoteArray(int7gram, 70.0)
oneDimArrayToMidi(song2gram, 'Midi/7gram_int.mid')