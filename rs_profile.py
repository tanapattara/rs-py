import pandas as pd

from util import getfile

ratingsdf = pd.read_csv("data/_rating.csv", sep='|')
venuedf = pd.read_csv("data/_venue.csv", sep='|')
categorydf = pd.read_csv("data/category.csv", sep='|')

# loop all user
