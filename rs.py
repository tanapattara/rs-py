from cgi import test
from unittest import result
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd

from rsknn import RSKNN

# load dataframe
ratingsdf = pd.read_csv("data/rating.csv", sep='|')
userdf = pd.read_csv("data/user.csv", sep='|')
venuedf = pd.read_csv("data/venue.csv", sep='|')

# train-test data
testdf = ratingsdf.sample(frac=0.1, replace=True, random_state=1)
traindf = pd.concat([ratingsdf,testdf]).drop_duplicates(keep=False)

knn = RSKNN(traindf, userdf, venuedf)

#loop all row in testdata
for index, row in testdf.iterrows():
    targetid = row['userid']
    targetvenue = row['venueid']
    targetscore = row['score']
    rec_ = knn.recommend2user(targetid, targetvenue)
    print(rec_)

