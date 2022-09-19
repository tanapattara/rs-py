from cgi import test
from unittest import result
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
from alive_progress import alive_bar

from rs_weighted_rating import RSWeightedRating
from rsknn import RSKNN


# load dataframe
ratingsdf = pd.read_csv("data/rating.csv", sep='|')
userdf = pd.read_csv("data/user.csv", sep='|')
venuedf = pd.read_csv("data/venue.csv", sep='|')

# train-test data
testdf = ratingsdf.sample(frac=0.1, replace=True, random_state=1)
traindf = pd.concat([ratingsdf,testdf]).drop_duplicates(keep=False)

rsw = RSWeightedRating()
weighted_venue = rsw.getDataframe(ratingsdf=ratingsdf, venuedf=venuedf)
print(weighted_venue.head(20))

# ratingdf -> venueid|userid|score|time|comment
# userdf -> userid|name|link|review
# venuedf -> venueid|name|location

# knn = RSKNN(traindf, userdf, venuedf)
#loop all row in testdata
for index, row in testdf.iterrows():
    targetid = row['userid']
    targetvenue = row['venueid']
    targetscore = row['score']

