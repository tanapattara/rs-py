#https://www.datacamp.com/tutorial/recommender-systems-python
from cgi import test
from unittest import result
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
from alive_progress import alive_bar
import os.path
import os
class RSWeightedRating():    
    
    # v is the number of votes for the movie;
    # m is the minimum votes required to be listed in the chart;
    # R is the average rating of the movie;
    # C is the mean vote across the whole report.
    def weighted_rating(self, x):
        v = x['vote_count']
        R = x['vote_average']
        # Calculation based on the IMDB formula
        return (v/(v+self.m) * R) + (self.m/(self.m+v) * self.C)
        
    def getDataframe(self, ratingsdf, venuedf):

        filepath = "data/venue_metadata.csv"
        if os.path.exists(filepath):
            existdata = pd.read_csv("data/rating.csv", sep='|', encoding='utf-8')
            return existdata

        # find metadata on venue row
        # venuedf -> venueid|name|location|vote_count|vote_average|
        vote_count = []
        vote_average = []
        with alive_bar(len(venuedf)) as bar:
            for index, row in venuedf.iterrows():
                venueid = row['venueid']
                # looking in ratingdf
                # ratingdf -> venueid|userid|score|time|comment
                target_v_df = ratingsdf.loc[ratingsdf['venueid'] == venueid]
                venue_vote_count = len(target_v_df.index)
                venue_vote_average = target_v_df['score'].sum() / venue_vote_count
                vote_count.append(venue_vote_count)
                vote_average.append(venue_vote_average)
                bar()

        newcol_count = np.array(vote_count)
        newcol_average = np.array(vote_average)
        venuedf['vote_count'] = newcol_count.tolist()
        venuedf['vote_average'] = newcol_average.tolist()

        self.m = venuedf['vote_count'].quantile(0.90)
        self.C = venuedf['vote_average'].mean()
        venuedf_data = venuedf.copy().loc[venuedf['vote_count'] >= self.m]

        # Define a new feature 'score' and calculate its value with `weighted_rating()`
        venuedf_data['score'] = venuedf_data.apply(self.weighted_rating, axis=1)
        #Sort venue based on score calculated above
        venuedf_data = venuedf_data.sort_values('score', ascending=False)
        venuedf_data.to_csv('data/venue_metadata.csv', sep='|', encoding='utf-8',index=False)
        #Print the top 20 venue
        # venuedf -> venueid|name|location|vote_count|vote_average|
        #venuedf_data[['venueid', 'name', 'vote_count', 'vote_average', 'score']].head(20)
        return venuedf_data