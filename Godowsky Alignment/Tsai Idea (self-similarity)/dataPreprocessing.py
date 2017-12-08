import sys
import os
sys.path.append(os.getcwd() + '/../..')

import selfSimilarityMatrix

# MIDI to CSV Files

godowskyPath = '../Godowtsai Dataset/Godowsky/'
chopinPath = '../Godowtsai Dataset/Chopin/'

selfSimilarityMatrix.midiToCSV([godowskyPath], 'Godowsky_CSVs/')
selfSimilarityMatrix.midiToCSV([chopinPath], 'Chopin_CSVs/')