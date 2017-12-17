import sys
import os
# add the path to selfSimilarityMatrix.py so we can import it
sys.path.append(os.getcwd() + '/../..')
import selfSimilarityMatrix

import math
import numpy as np
import itertools
from PIL import Image
import pretty_midi


def SelfSimilarityAlignment(SS1, SS2, steps, weights, subsequence):
	'''
	Take in two self similarity matrices (SSOne, and SSTwo)

	SSOne: The first self similarity matrix to align
	SSTwo: The second self similarity matrix to align
	steps: Possible steps you can take in your alignment
			an np array with two rows, the first row is the steps you can take in SSOne
			the second row is the associated steps you can take in SSTwo
	weights: Corresponding weights for each step
	subsequence: whether to do subsequence alignment or a full alignment (whether have to match up (0,0) and (end, end))
	'''

	# get the length of each Self Similarity Matrix
	SS1Length = SS1.shape[0] # assume they're square matrices
	SS2Length = SS2.shape[0]

	# Make the path and cumulative cost array
	# the path array is a 2-d array	
	# Rows correspond to indices of SS1, cols correspond to indices of SS2
	pathArray = np.zeros((SS1Length, SS2Length)).tolist() # list so that can put variable length paths in it
	pathArray[0][0] = np.array([[0], [0]]) # default path starting at (0,0)
	cumulativeCostArray = np.zeros((SS1Length, SS2Length))

	# fill the path array if it's subsequence matching
	if subsequence:
		# SS1 is the subsequence, so can start at any column
		for i in range(SS2Length):
			pathArray[0][i] = np.array([[0], [i]])
			cumulativeCostArray[0, i] = PathToMarginalCost(SS1, SS2, pathArray[0][i])

	# fill the accumulated cost matrix by going down each column at a time
	for row in range(SS1Length):
		for col in range(SS2Length):
			print('Row, Col: %d, %d'%(row, col))
			print('Percent done: %f'%((row * SS1Length + col) / (SS1Length * SS2Length) * 100))
			print(cumulativeCostArray[1][1])
			if not (row == 0 and col == 0) and not (subsequence and row == 0):
				# loop through each possible step
				bestCost = np.inf
				bestCostIndex = 0
				bestPath = []

				for stepIndex in range(steps.shape[1]):

					curStepRow = steps[0, stepIndex]
					curStepCol = steps[1, stepIndex]

					# check the spot you're looking back at is 
					if (not((row - curStepRow) < 0 or (col - curStepCol) < 0)):
						curPath = pathArray[row - curStepRow][col-curStepCol]
						# Make sure it's been filled in with a path
						if isinstance(curPath, np.ndarray):
							# it's an unreachable spot you've looked back into
							newStep = np.array([[row],[col]])
							appendedPath = np.append(curPath, newStep, axis=1)
	
							#!!! switch out this one so can deal with dif weights, have it be a kind of subsampling thing
							#newCost = PathToCost(SS1, SS2, appendedPath) # think about whether this is legit - would want to subsample the new ones - at the moment doesn't use the accumulated cost at all
							marginalCost = PathToMarginalCost(SS1, SS2, appendedPath)
							print("marginal cost: %f"%marginalCost)
							newCost = cumulativeCostArray[row - curStepRow, col - curStepCol] + marginalCost * weights[stepIndex]

							if newCost <= bestCost:
								bestCost = newCost
								bestPath = appendedPath

				# if you're best cost is still inf, then put the path for this location as inf
				# this marks it as an unreachable location
				if (bestCost == np.inf):
					print("no path for this location")
					pathArray[row][col] = np.inf
					cumulativeCostArray[row, col] = np.inf
				else:
					pathArray[row][col] = bestPath
					cumulativeCostArray[row, col] = bestCost # think about whether this is legit

	# print(pathArray)
	# print(cumulativeCostArray)

	return pathArray, cumulativeCostArray


def PathToMarginalCost(SS1, SS2, path):
	'''
	Find the cost associated with the last step in the path
	'''

	# assumes symmetry of SS1 and SS2 I think? also that
	# we have non-decreasing indices

	# pull out the sub-matrix
	SS1Indices = path[0, :]
	SS2Indices = path[1, :]

	# pull out the most reason addition to the path
	lastIndex1 = SS1Indices[-1]
	lastIndex2 = SS2Indices[-1]

	newRow1 = SS1[lastIndex1, SS1Indices]
	newCol1 = SS1[SS1Indices, lastIndex1]
	# remove the last one from 1 of them to avoid double counting the overlap
	newCol1 = newCol1[0:-1]

	newRow2 = SS2[lastIndex2, SS2Indices]
	newCol2 = SS2[SS2Indices, lastIndex2]
	# remove the last one from 1 of them to avoid double counting the overlap
	newCol2 = newCol2[0:-1]

	# marginal cost is the sum of squares between them
	marginalCost = np.sum(np.square(newRow1 - newRow2)) + np.sum(np.square(newCol1 - newCol2))

	return marginalCost

def SubSampleSS(SS1, SS2, path):
	'''
	Subsample SS1 and SS2 according to the path

	SSOne: the first self similarity matrix
	SSTwo: the second self similarity matrix
	Path: The path in the alignment. 
			an np array with two rows. The first row corresponds
			to the indices of SSOne we're sampling, the second corresponds
			to the indices of SSTwo we're sampling

	'''
	# pull out the sub-matrix
	SS1Indices = path[0, :]
	SS2Indices = path[1, :]

	# get the permutations with repetition of the indices (all the intersections that we want to subsample out)
	# this outputs a list of tuples
	SS1Permutations = [p for p in itertools.product(SS1Indices, repeat=2)]
	SS2Permutations = [p for p in itertools.product(SS2Indices, repeat=2)]

	# pull out the first element from each tuple - this is your "row" for each subsampled cell
	SS1IndicesOne = [i[0] for i in SS1Permutations]
	SS2IndicesOne = [i[0] for i in SS2Permutations]
	# pull out the second element from each tuple - this is your "col" for each subsampled cell
	SS1IndicesTwo = [i[1] for i in SS1Permutations]
	SS2IndicesTwo = [i[1] for i in SS2Permutations]

	# pull out the sub matrices
	subsampledSS1 = SS1[SS1IndicesOne, SS1IndicesTwo].reshape(path.shape[1], path.shape[1])
	subsampledSS2 = SS2[SS2IndicesOne, SS2IndicesTwo].reshape(path.shape[1], path.shape[1])

	return subsampledSS1, subsampledSS2


def PathToCost(SS1, SS2, path):
	'''
	Take in two self similarity matrices and a partial (or full) alignment
	and output the cost of this alignment

	SSOne: the first self similarity matrix
	SSTwo: the second self similarity matrix
	Path: The path in the alignment. 
			an np array with two rows. The first row corresponds
			to the indices of SSOne we're sampling, the second corresponds
			to the indices of SSTwo we're sampling

	Output: The sum of squared differences between the sub-self-similarity matrices
			drawn based on the indices in the path

	Example:
	SSOne: (0 0 1    
			1 1 0
			1 1 0) 
	
	SSTwo: (0 0 0 0 1 1
			0 0 0 0 1 1
			1 1 1 1 0 0
			1 1 1 1 0 0
			1 1 1 1 0 0
			1 1 1 1 0 0)

	Path: (0 1
		   0 2)

	Sampled Sub matrices:

	SSOneSub: (0 0
			   1 1)

	SSTwoSub: (0 0
			   1 1)

	Cost: 0

	Path: (0 0
		   0 3)

	SSOneSub: (0 0
			   0 0)

	SSTwoSub: (0 0
			   1 1)

	Cost: 1^2 + 1^2 = 2
	'''
	# pull out the sub matrices
	subsampledSS1, subsampledSS2 = SubSampleSS(SS1, SS2, path)

	# the cost is the L2 norm of the difference between our sub matrices
	difference = subsampledSS1 - subsampledSS2
	cost = np.sum(np.square(difference))
	return cost

def alignedMidis(songPath, timesOne, timesTwo, outFile):
	midiData = pretty_midi.PrettyMIDI(songPath)
	midiData.adjust_times(timesOne, timesTwo)
	midiData.write(outFile)



fileOne = '../Godowtsai Dataset/Edited Godowsky/godowsky_v1_chopin_op10_e01_edited.mid'
fileTwo = '../Godowtsai Dataset/Edited Chopin/chopin_op10_e01_edited.mid'

SS1, matrixRepOne = selfSimilarityMatrix.midiToSimilarityAndMatrixRep(fileOne)
SS2, matrixRepTwo = selfSimilarityMatrix.midiToSimilarityAndMatrixRep(fileTwo)

im = Image.fromarray(matrixRepOne.astype('float') * 255)
im.show()
im = Image.fromarray(matrixRepTwo.astype('float') * 255)
im.show()


steps = np.array([[1, 1, 2], [1, 2, 1]])
weights = np.array([1, 1, 1])
subsequence = False

pathArray, cumulativeCost = SelfSimilarityAlignment(SS1, SS2, steps, weights, subsequence)
# deal with infinities in cumulativeCost
cumulativeCost[cumulativeCost == np.inf] = -1

fs = 100


# #### old stuff below
# # make a self-similarity matrix from the CSVs that have the MIDI data
# fileOne = 'Godowsky_CSVs/godowsky_v1_chopin_op10_e01.csv'
# fileTwo = 'Chopin_CSVs/chopin_op10_e01.csv' 

# SS1, matrixRepOne = selfSimilarityMatrix.csvToSelfSimilarityAndMatrixRep(fileOne, True) # onsetOnly
# SS2, matrixRepTwo = selfSimilarityMatrix.csvToSelfSimilarityAndMatrixRep(fileTwo, True)


# steps = np.array([[1, 1, 2], [1, 2, 1]])
# weights = np.array([1, 1.2247, 1.2247])
# subsequence = False

# pathArray, cumulativeCost = SelfSimilarityAlignment(SS1, SS2, steps, weights, subsequence)
# # deal with infinities in cumulativeCost
# cumulativeCost[cumulativeCost == np.inf] = -1

# ###############################################
# post processing of the path and cost matrices


# find the minimum cumulative cost at the bottom (tells you where your subsequence ends)
minIndex = np.argmin(cumulativeCost[-1,:])
# get the path corresponding to the minimum
if subsequence:
	minPath = pathArray[-1][minIndex]
else:
	minPath = pathArray[-1][-1]
	if cumulativeCost[-1][-1] == -1:
		print("This alignment was impossible (no path to reach bottom corner)")

pathRows = minPath[0,:]
pathCols = minPath[1,:]

# make audio output
fs = 10.
rowTimes = pathRows * 1/fs
colTimes = pathCols * 1/fs
alignedMidis(fileTwo, colTimes, rowTimes, 'temp.mid')

# plot the minimum path
fig = plt.figure(figsize=(7, 4))
myPlot = fig.add_subplot(111)
myPlot.plot(pathCols, pathRows, '-', label="Path")
myPlot.set_xlabel("Frame in Song Two")
myPlot.set_ylabel("Frame in Song One")

myPlot.set_title("Alignment")
myPlot.legend(loc="best", frameon=False)
myPlot.axis('equal')
# Write the figure
fig.savefig('pathPlot')

# visualize the cumulative cost matrix
im = Image.fromarray(cumulativeCost / np.max(cumulativeCost) * 255)
im.show()

# index out the frames from each and display side by side - all rows because we want all pitches, pulling out different time stamps
framesFromOne = matrixRepOne[:, pathRows]
framesFromTwo = matrixRepTwo[:, pathCols]

# convert the boolean array of onsets to integers
framesFromOneFloat = framesFromOne.astype('float')
framesFromTwoFloat = framesFromTwo.astype('float')

lengthDif = matrixRepTwo.shape[1] - matrixRepOne.shape[1]
paddedSongOne = np.append(matrixRepOne, np.zeros((matrixRepOne.shape[0], lengthDif)), axis=1)
groupedSongsBefore = np.append(np.append(paddedSongOne, np.zeros((40, paddedSongOne.shape[1])), axis=0), matrixRepTwo, axis=0)


# concatenate onto each other so can see them both - space by a thing of 0s
groupedSongsAfter = np.append(np.append(framesFromOneFloat, np.zeros((40, framesFromOneFloat.shape[1])), axis=0), framesFromTwoFloat, axis=0)

im = Image.fromarray(framesFromOneFloat * 255)
im.show()
im = Image.fromarray(framesFromTwoFloat * 255)
im.show()
im = Image.fromarray(groupedSongsAfter * 255)
im.show()
im = Image.fromarray(groupedSongsBefore * 255)
im.show()


# plot ground truth - hard coding in the ground truth for now
# rowGroundTruthTimes = []
# colGroundTruthTimes = []

# fig = plt.figure(figsize=(7, 4))
# myPlot = fig.add_subplot(111)
# myPlot.plot(colTimes, rowTimes, '-', label="Algorithmic Alignment")
# myPlot.plot(colGroundTruthTimes, rowGroundTruthTimes, '.', label='Ground Truth')
# myPlot.set_xlabel("Frame in Song Two")
# myPlot.set_ylabel("Frame in Song One")

# myPlot.set_title("Alignment")
# myPlot.legend(loc="best", frameon=False)
# myPlot.axis('equal')
# # Write the figure
# fig.savefig('groundTruthPlot')

# test case
# SS1 = np.array([[0, 0, 1], [1, 1, 0], [1, 1, 0]])
# SS2 = np.array([[0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0]])
# path = np.array([[0, 0], [0, 3]])
# # cost = PathToCost(SS1, SS2, path)

# steps = np.array([[1, 1, 2], [1, 2, 1]])
# weights = np.array([1, 1, 1])

# SelfSimilarityAlignment(SS1, SS2, steps, weights, True)

