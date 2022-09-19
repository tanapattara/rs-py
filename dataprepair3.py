"""
clean venue
"""
from tokenize import Number
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import warnings
import os
import collections.abc

from alive_progress import alive_bar
from os import listdir
from os.path import isfile, join

venuedf = pd.read_csv("data/venue.csv", sep="|")
userdf = pd.read_csv("data/user.csv", sep="|")
ratingdf = pd.read_csv("data/rating.csv", sep="|")

## the above venue has very low dataset. We will use bayesian average
venue_stats = ratingsdf.groupby('venueid')[['score']].agg(['count', 'mean'])
venue_stats.columns = venue_stats.columns.droplevel()
venue_stats = venue_stats.sort_values(by = 'count')
print(venue_stats)

user_stats = ratingsdf.groupby('userid')[['score']].agg(['count','mean'])
user_stats.columns = user_stats.columns.droplevel()
user_stats = user_stats.sort_values(by = 'count')
print(user_stats)