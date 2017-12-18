# Godowtsai Dataset

## Chopin
Contains MIDI files for chopin etudes from Op. 10 and 25. Data is from sources specified in Soruces of Data doc.

## Godowsky
Contains MIDI files Godowsky versions of Chopin etudes. Some songs have multiple versions, which are specified in the file names, and etudes that just have version are marked v1.

## Edited Chopin
Edited MIDI files that remove the initial silence from the files in Chopin folder.

## Edited Godowsky
Edited MIDI files that remove the initial silence from the files in Godowsky folder.

## Ground Truth Alignments
Contains CSV files that contain alignments. The format of the file is the time in Chopin piece that should correspond to a time in the Godowsky piece (where the Chopin piece is modified).
Ex.
0,0
1,1.2
...
