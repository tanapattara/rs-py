from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd


ratingsdf = pd.read_csv("data/rating.csv", sep='|')
userdf = pd.read_csv("data/user.csv", sep='|')
venuedf = pd.read_csv("data/venue.csv", sep='|')

class RSKNN:
    # init method or constructor
    def __init__(self, ratingsdf, userdf, venuedf, k=10, metric='cosine'):
        self.ratingsdf = ratingsdf
        self.userdf = userdf
        self.venuedf = venuedf
        self.k = k
        self.metric = metric

    def recommend(self):
        N = len(self.ratingsdf['userid'].unique())
        M = len(self.ratingsdf['venueid'].unique())
        
        # Map Ids to indices
        self.user_mapper = dict(zip(np.unique(self.ratingsdf["userid"]), list(range(N))))
        self.venue_mapper = dict(zip(np.unique(self.ratingsdf["venueid"]), list(range(M))))
        
        # Map indices to IDs
        self.user_inv_mapper = dict(zip(list(range(N)), np.unique(self.ratingsdf["userid"])))
        self.venue_inv_mapper = dict(zip(list(range(M)), np.unique(self.ratingsdf["venueid"])))
        
        user_index = [self.user_mapper[i] for i in self.ratingsdf['userid']]
        venue_index = [self.venue_mapper[i] for i in self.ratingsdf['venueid']]

        self.X = csr_matrix((self.ratingsdf["score"], (venue_index, user_index)), shape=(M, N))    

        venues_name = dict(zip(self.venuedf['venueid'], self.venuedf['name']))  
        venue_id = 3
        # find similarity of vanue
        similar_ids = self.find_similar_venue(venue_id)
        # display result
        venue_name = venues_name[venue_id]
        print(f"Since you go {venue_name}")
        for i in similar_ids:
            print(venues_name[i])

    """
    Find similar venue using KNN
    """
    def find_similar_venue(self, venue_id):
        
        neighbour_ids = []
        
        venue_ind = self.venue_mapper[venue_id]
        venue_vec = self.X[venue_ind]
        
        self.k+=1
        kNN = NearestNeighbors(n_neighbors=self.k, algorithm="brute", metric=self.metric)
        kNN.fit(self.X)
        venue_vec = venue_vec.reshape(1,-1)
        neighbour = kNN.kneighbors(venue_vec, return_distance=False)
        for i in range(0, self.k):
            n = neighbour.item(i)
            neighbour_ids.append(self.venue_inv_mapper[n])
        neighbour_ids.pop(0)
        return neighbour_ids


knn = RSKNN(ratingsdf, userdf, venuedf)
knn.recommend()