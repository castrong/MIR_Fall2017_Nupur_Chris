import numpy as np

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
	keys = [key for key, value in noteToColumnDict.iteritems() if value == col]
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
		print(choice)
		seq = seq + [colToNote(choice, noteToColumnDict)]
		# update distribution
		curDistribution = transitionMatrix.dot(curDistribution)

	# map from column numbers back to notes
	return seq

# test
bigramList = [((0,1), 3), ((0,2), 4), ((0,3), 2), ((1,2), 2), ((1,3), 4), ((2,3), 2), ((2,2), 1), ((3,0), 1)]
matrix, noteToCol = generateTransitionMatrix(bigramList)

steadyState = getSteadyStateDistribution(matrix, np.array([1,0,0,0]))

seq = generateSequenceFromTransitionMatrix(matrix, noteToCol, np.array([1,0,0,0]), 100)
