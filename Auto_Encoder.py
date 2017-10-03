# WRITTEN BY MINT

from mido import MidiFile
import os
import csv

import numpy as np
from PIL import Image

# keras specific imports
from keras.models import Sequential
from keras.layers import Activation, Dense

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

def sampleFromMatrix(matrix_in, sample_rows, sample_cols):
    '''
    Sample a sub-matrix from a matrix
    Input: a matrix of size mxn and the dimensions of the sample
    Output: a randomly selected sample of size sample_rows x sample_cols that is entirely contained within matrixIn
    '''
    in_rows = matrix_in.shape[0]
    in_cols = matrix_in.shape[1]
    # select a start row and column for your submatrix
    start_row = np.random.randint(in_rows - sample_rows + 1) # not inclusive, so between 0 and inRows - sample_rows inclusive
    start_col = np.random.randint(in_cols - sample_cols + 1)
    return matrix_in[start_row:(start_row + sample_rows), start_col:(start_col + sample_cols)]

def getSamplesFromSong(song_matrix, num_samples, sample_rows, sample_cols):
    '''
    Get many samples from a song, and output a matrix where each row corresponds to a sample
    Input: song_matrix - a 2-d matrix where the rows correspond to pitch and the cols correspond to time. We'll sample from this
           num_samples - the number of samples to Take
           sample_rows - rows in the sample
           sample_cols - columns in the sample
    Output: A 2-d matrix, where each row corresponds to an "unwrapped sample"
            where "unwrapping" is taking the 2-d sample and rolling it out into a row.
            Columns are iterated over first then rows e.g x = [1, 2] becomes [1, 2, 3, 4]
                                                               [3, 4]
    '''
    # make an empty matrix to store your samples
    sample_matrix = np.empty((num_samples, sample_rows * sample_cols))
    # Sample, unwrap, and store in sample_matrix num_samples times
    for i in range(num_samples):
        cur_sample = sampleFromMatrix(song_matrix, sample_rows, sample_cols)
        unwrapped_sample = np.reshape(cur_sample, (1, -1)) # -1 lets it decide that dimension
        sample_matrix[i, :] = unwrapped_sample
    return sample_matrix


'''
Set some parameters
'''
# min 1, max 128
sample_rows = 128
# min 1, max depends on chunk size when turn into a matrix
sample_cols = 50

num_training_samples = 10000
num_validation_samples = 2000

num_epochs = 5
batch_size = 128

time_per_chunk = 0.1

'''
Preprocessing - getting a binary of note onsets
'''
# get the CSV files, then create an np array from one CSV file
#midiToCSV(['MidiFiles/'], 'CSV_From_Midi/')
song_matrix = createMatrixFromCSV('./CSV_From_Midi/original_MidiFiles.csv', True, timePerChunk=time_per_chunk)

# pull out the velocity (ignore duration, which is at index 0 in the 3rd dimension)
velocity_only = song_matrix[:,:, 1] # pick out just the velocity
# turn into binary based on whether 0 or not
velocity_only_binary = (velocity_only > 0).astype(float)

# visualize your matrix
im = Image.fromarray(velocity_only_binary * 256)
im.show()

'''
Create a training and validation dataset
'''

X_train = getSamplesFromSong(velocity_only_binary, num_training_samples, sample_rows, sample_cols)
# note validation may contain some exact copies of training
X_val = getSamplesFromSong(velocity_only_binary, num_validation_samples, sample_rows, sample_cols)

'''
Set up our keras model of an autoencoder
'''
# create the model
model = Sequential()
# add layers
model.add(Dense(units=64, input_dim=sample_rows * sample_cols))
model.add(Activation('relu'))
model.add(Dense(units=sample_rows * sample_cols)) # output the same dim as the original input
model.add(Activation('relu')) # not sure if should activate here

# set the loss and optimizer
model.compile(loss='mean_squared_error',
                optimizer='sgd')


'''
Train our model
'''
model.fit(X_train, X_train, epochs=num_epochs, batch_size=batch_size)



'''
Analyze the weights of our model
'''

weights = model.get_weights()
layer_one_weights = weights[0]
layer_two_weights = weights[1]

num_to_display = 3
for i in range(num_to_display):
    # get a single filter
    curFilter = np.reshape(layer_one_weights[:, i], (sample_rows, sample_cols))
    # display as an image
    im = Image.fromarray(curFilter * 256. / np.mean(curFilter)) # scale so fills whole range
    im.show()






