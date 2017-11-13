import csv
import numpy as np
import pyximport; pyximport.install(setup_args={'include_dirs': [np.get_include()]})
import dtw

from mido import Message, MidiFile, MidiTrack


import os
import scipy.io as sp
import random
import mido

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

'''
For a logical matrix, deletes columns where there are zeros in the given array

Test:
testMat = np.array([[ True, False, False,  True],
	   [False, False,  True, False],
	   [False,  True, False, False]])

cols = np.array([0,3,4,0])

out = deleteGivenColumns(testMat, cols)
print(out)
'''
def deleteGivenColumns(logicalMat, columnsToDelete):
	for i in range(columnsToDelete.shape[0]-1, -1, -1):
		if columnsToDelete[i] == 0:
			logicalMat = np.delete(logicalMat, i, 1)
	return logicalMat

'''
Calculates cosimilarity between two logical matrices. True represents
a note being on, and False means the note is off.

The first matrix is on the x axis, and the second is on the y axis. Each
entry in the matrix is a value between 0 and 1, where 0 means there are no
notes in common for that frame, and 1 means that all of the notes played
in that frame are the same.

Test:

mat1 = np.array([[ False, False,  True],
	   [True, False,  True],
	   [False,  True, False]])

mat2 = np.array([[ True, False],
	   [False,  True],
	   [True,  True]])

cosimilarity(mat1, mat2)

with hopsize 1
output should match matrix:
[[2/3, 2/3, 1/2], [0, 2/3, 1/2]]
'''

def findCosimilarityMatrix(mat1, mat2):
	hopsize = 1

	length1 = np.shape(mat1)[1]
	length2 = np.shape(mat2)[1]

	height = np.shape(mat1)[0]

	simCols = length1 - hopsize + 1
	simRows = length2 - hopsize + 1

	print(simRows)
	print(simCols)

	cosimilarityMat = np.empty([simRows,simCols])

	for i in range(simRows):
		A = mat2[:height, i:i+hopsize]
		aOn = np.sum(A)

		for j in range(simCols):
			B = mat1[:height, j:j+hopsize]
			bOn = np.sum(B)

			sameOn = np.sum(np.logical_and(A,B))

			similarity = (2 * sameOn) / (aOn + bOn)

			cosimilarityMat[i][j] = similarity

	# vertically flip because similarity matrices are defined stupidly
	cosimilarityMat = np.flipud(cosimilarityMat)

	return cosimilarityMat

def findCosimilarityWithPitchShifts(mat1, mat2, numPitchShifts):
	hopsize = 1

	up = mat2
	down = mat2

	length1 = np.shape(mat1)[1]
	length2 = np.shape(mat2)[1]

	height = np.shape(mat1)[0]

	simCols = length1 - hopsize + 1
	simRows = length2 - hopsize + 1

	cosimilarityMat = findCosimilarityMatrix(mat1, mat2)
	bestMetric = findCosimilarityMetric(cosimilarityMat)

	rowOfZeros = np.zeros(length2)

	# shift up
	for i in range(numPitchShifts):
		up = np.delete(up,0,0)
		up = np.vstack([up,rowOfZeros])

		currentMat = findCosimilarityMatrix(mat1, up)
		currentMetric = findCosimilarityMetric(currentMat)

		if currentMetric > bestMetric:
			cosimilarityMat = currentMat
			bestMetric = currentMetric

	# shift down
	for i in range(numPitchShifts):
		down = np.delete(up,height-1,0)
		down = np.vstack([rowOfZeros,up])

		currentMat = findCosimilarityMatrix(mat1, down)
		currentMetric = findCosimilarityMetric(currentMat)

		if currentMetric > bestMetric:
			cosimilarityMat = currentMat
			bestMetric = currentMetric

	im = Image.fromarray(cosimilarityMat * 256)
	im.show()

	return cosimilarityMat

def findCosimilarityMetric(mat):
	return np.average(mat)

def costAndOnsetsToMIDI(cost, onsetOnlyOne, onsetOnlyTwo):

	# cost = np.array([[5,9,9,9], [9,8,2,9], [9,9,5,3]], dtype=np.float64)

	dn = np.array([0,1,2,1], dtype=np.uint32) # allowed steps along the rows
	dm = np.array([1,2,1,3], dtype=np.uint32) # allowed steps along the cols
	dw = np.array([1.0, 1.0, 2.0, 3.0]) # weight of each step
	subsequence = False # do subsequence matching
	# create a dictionary that holds your parameters - you'll send this to the DTW function
	parameter = {'dn': dn, 'dm': dm, 'dw': dw, 'SubSequence': subsequence}

	[accumCost, steps] = dtw.DTW_Cost_To_AccumCostAndSteps(cost, parameter)
	[path, endCol, endCost] = dtw.DTW_GetPath(accumCost, steps, parameter)

	# drawing from arrays onsetOnlyOne and onsetOnlyTwo
	# onsetOnlyOne = np.random.randint(2, size=(121, 100))
	# onsetOnlyTwo = np.random.randint(2, size=(121, 200))
	# path = np.array([[0,0,0,0,0,0,0,0,0,0,3,5], [0,1,2,3,4,5,6,7,8,9,10,11]])

	# create a MIDI file with two tracks
	mid = MidiFile()
	trackOne = MidiTrack()
	trackTwo = MidiTrack()
	mid.tracks.append(trackOne)
	mid.tracks.append(trackTwo)

	for i in range(path.shape[1]):
		pathRow = path[0,i]
		pathCol = path[1,i]

		# grab the corresponding frames
		frameOne = onsetOnlyOne[:, pathRow]
		frameTwo = onsetOnlyTwo[:, pathCol]

		# assume the frames are the same length
		# add a note on for any location in the frame that's true
		onsetsOne = np.argwhere(frameOne > 0)
		onsetsTwo = np.argwhere(frameTwo > 0)
		# start the notes from track one
		print(onsetsOne)
		for i in range(len(onsetsOne)):
			msg1 = Message('note_on', note=int(onsetsOne[i]), velocity=60, time=0)
			trackOne.append(msg1)
		# start the notes from track two
		for i in range(len(onsetsTwo)):
			msg1 = Message('note_on', note=int(onsetsTwo[i]), velocity=60, time=0)
			trackTwo.append(msg1)


		delayDone = False
		# end the notes from track one
		for i in range(len(onsetsOne)):
			if not delayDone:
				delayDone = True
				msg1 = Message('note_on', note=int(onsetsOne[i]), velocity=0, time=80) # delay
			else:
				msg1 = Message('note_on', note=int(onsetsOne[i]), velocity=0, time=0)
			trackOne.append(msg1)

		delayDone = False
		# end the notes from track two
		for i in range(len(onsetsTwo)):
			if not delayDone:
				delayDone = True
				msg1 = Message('note_on', note=int(onsetsTwo[i]), velocity=0, time=80) # delay
			else:
				msg1 = Message('note_on', note=int(onsetsTwo[i]), velocity=0, time=0)
			trackTwo.append(msg1)

	mid.save('test.mid')



#midiToCSV(['Midi/'], 'CSV_From_Midi/')
origMatrix = createMatrixFromCSV('CSV_From_Midi/chpn_op10_e01.csv', True)
origVelocityOnly = origMatrix[:,:, 1] # pick out just the velocity
origLogicalMat = origVelocityOnly.astype(bool)
origOneDimWithZeros = generateOneDimArray(origLogicalMat) # zeros where we want to delete columns
origOnsetOnly = deleteGivenColumns(origLogicalMat, origOneDimWithZeros)


godMatrix = createMatrixFromCSV('CSV_From_Midi/godowsky_chopin_etude_10_01_v1_(c)yogore.csv', True)
godVelocityOnly = godMatrix[:,:, 1] # pick out just the velocity
godLogicalMat = godVelocityOnly.astype(bool)
godOneDimWithZeros = generateOneDimArray(godLogicalMat) # zeros where we want to delete columns
godOnsetOnly = deleteGivenColumns(godLogicalMat, godOneDimWithZeros)

cosimilarityMat = findCosimilarityWithPitchShifts(origOnsetOnly, godOnsetOnly, 2)


costAndOnsetsToMIDI(cosimilarityMat, origOnsetOnly, godOnsetOnly)

