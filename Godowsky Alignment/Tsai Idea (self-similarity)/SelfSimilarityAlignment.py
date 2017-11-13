import sys
import os
# add the path to selfSimilarityMatrix.py so we can import it
sys.path.append(os.getcwd() + '/../..')
import selfSimilarityMatrix


import numpy as np
import itertools

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
							newCost = cumulativeCostArray[row - curStepRow, col - curStepCol] + marginalCost


							if newCost <= bestCost:
								bestCost = newCost
								bestPath = appendedPath

				# if you're best cost is still inf, then put the path for this location as inf
				# this marks it as an unreachable location
				if (bestCost == np.inf):
					print("infinite cost at (%d, %d)"%(row, col))
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
	return np.sum(np.square(newRow1 - newRow2)) + np.sum(np.square(newCol1 - newCol2))

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




# SS1 = np.array([[0, 0, 1], [1, 1, 0], [1, 1, 0]])
# SS2 = np.array([[0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0]])
# path = np.array([[0, 0], [0, 3]])
# # cost = PathToCost(SS1, SS2, path)

# steps = np.array([[1, 1, 2], [1, 2, 1]])
# weights = np.array([1, 1, 1])

# SelfSimilarityAlignment(SS1, SS2, steps, weights, True)


# make a self-similarity matrix from the CSVs that have the MIDI data
fileOne = 'Godowsky_CSVs/godowsky_v1_chopin_op10_e01.csv'
fileTwo = 'Godowsky_CSVs/godowsky_v1_chopin_op10_e01.csv'

SS1 = selfSimilarityMatrix.csvToSelfSimilarity(fileOne, True) # onsetOnly
SS2 = selfSimilarityMatrix.csvToSelfSimilarity(fileTwo, True)


steps = np.array([[1, 0, 1, 1, 2], [0, 1, 1, 2, 1]])
weights = np.array([1, 1, 1])

pathArray, cumulativeCost = SelfSimilarityAlignment(SS1, SS2, steps, weights, True)

from PIL import Image
im = Image.fromarray(cumulativeCost)
im.show()

