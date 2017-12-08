# WRITTEN BY MINT

from mido import MidiFile
import os
import csv

directories = ['MidiFiles/']
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
                outFileName = 'processed/'+name[0]+'_'+directory[:-1]+'.csv'
                with open(outFileName, 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    for row in noteonList:
                        spamwriter.writerow(row)