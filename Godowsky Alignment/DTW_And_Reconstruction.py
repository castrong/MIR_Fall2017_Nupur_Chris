import numpy as np
import pyximport; pyximport.install(setup_args={'include_dirs': [np.get_include()]})
import dtw

from mido import Message, MidiFile, MidiTrack


def costAndOnsetsToMIDI(cost, onsetOnlyOne, onsetOnlyTwo):

	# cost = np.array([[5,9,9,9], [9,8,2,9], [9,9,5,3]], dtype=np.float64)

	dn = np.array([1,1,2,1], dtype=np.uint32) # allowed steps along the rows
	dm = np.array([1,2,1,3], dtype=np.uint32) # allowed steps along the cols
	dw = np.array([1.0, 1.0, 2.0, 3.0]) # weight of each step
	subsequence = True # do subsequence matching
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


