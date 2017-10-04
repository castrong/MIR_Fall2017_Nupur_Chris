import csv
import numpy as np
import os
import scipy.io as sp
import random

from PIL import Image

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

			similarity = (2 * sameOn) / (aOn + bOn)

			similarityMat[i][j] = similarity

	# vertically flip because similarity matrixes are defined stupidly
	similarityMat = np.flipud(similarityMat)

	im = Image.fromarray(similarityMat * 256)
	im.show()

	return similarityMat



origMatrix = createMatrixFromCSV('random1_MidiFiles.csv', True)

origVelocityOnly = randMatrix[:,:, 1] # pick out just the velocity

im = Image.fromarray(origVelocityOnly * 2)
im.show()

origLogicalMat = origVelocityOnly.astype(bool)

origSim = similarity(origLogicalMat)
