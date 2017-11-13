import csv
import numpy as np
import os
import scipy.io as sp
import random
import mido

from PIL import Image
from mido import Message, MidiFile, MidiTrack

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
                    outFileName = directoryOut +name[0]+'.csv'
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

def similarity(mat):
	hopsize = 2

	width = np.shape(mat)[1]
	height = np.shape(mat)[0]

	print(width)

	size = width - hopsize + 1

	similarityMat = np.empty([size,size])

	for i in range(size):
		A = mat[:height, i:i+hopsize]
		aOn = np.sum(A)

		for j in range(size):
			B = mat[:height, j:j+hopsize]
			bOn = np.sum(B)

			sameOn = np.sum(np.logical_and(A,B))

			if (aOn == 0 and bOn == 0)
				similarity = 1
			else
				similarity = (2 * sameOn) / (aOn + bOn)

			similarityMat[i][j] = similarity

	# vertically flip because similarity matrices are defined stupidly
	similarityMat = np.flipud(similarityMat)

	#im = Image.fromarray(similarityMat * 256)
	#im.show()

	return similarityMat

def csvToSelfSimilarity(filename, onsetOnly):
	'''
	Take in the path to a CSV file that contains the MIDI data
	Output a self-similarity matrix from that MIDI file

	filename:
	'''
	# ahhhh think about time per chunk at some point
	origMatrix = createMatrixFromCSV(filename, onsetOnly)
	origVelocityOnly = origMatrix[:, :, 1]
	origLogicalMat = origVelocityOnly.astype(bool)
	origSim = similarity(origLogicalMat)
	return origSim

# midiToCSV(['Midi/'], 'CSV_From_Midi/')
# origMatrix = createMatrixFromCSV('godowsky_chopin_etude_10_01_v1_(c)yogore.csv', True)

# origVelocityOnly = origMatrix[:,:, 1] # pick out just the velocity

# im = Image.fromarray(origVelocityOnly * 2)
# im.show()

# origLogicalMat = origVelocityOnly.astype(bool)

# origSim = similarity(origLogicalMat)
