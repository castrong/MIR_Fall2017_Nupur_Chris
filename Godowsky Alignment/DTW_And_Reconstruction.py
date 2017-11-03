import numpy as np
import pyximport; pyximport.install()
import dtw

cost = np.array([[5,9,9,9], [9,8,2,9], [9,9,5,3]], dtype=np.float64)

dn = np.array([1,1,2,1], dtype=np.uint32) # allowed steps along the rows
dm = np.array([1,2,1,3], dtype=np.uint32) # allowed steps along the cols
dw = np.array([1.0, 1.0, 2.0, 3.0]) # weight of each step
subsequence = True # do subsequence matching
# create a dictionary that holds your parameters - you'll send this to the DTW function
parameter = {'dn': dn, 'dm': dm, 'dw': dw, 'SubSequence': subsequence}

[accumCost, steps] = dtw.DTW_Cost_To_AccumCostAndSteps(cost, parameter)
[path, endCol, endCost] = dtw.DTW_GetPath(accumCost, steps, parameter)
