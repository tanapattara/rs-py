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
        self.user_mapper = dict(
            zip(np.unique(self.ratingsdf["userid"]), list(range(N))))
        self.venue_mapper = dict(
            zip(np.unique(self.ratingsdf["venueid"]), list(range(M))))

        # Map indices to IDs
        self.user_inv_mapper = dict(
            zip(list(range(N)), np.unique(self.ratingsdf["userid"])))
        self.venue_inv_mapper = dict(
            zip(list(range(M)), np.unique(self.ratingsdf["venueid"])))

        user_index = [self.user_mapper[i] for i in self.ratingsdf['userid']]
        venue_index = [self.venue_mapper[i] for i in self.ratingsdf['venueid']]

        self.X = csr_matrix(
            (self.ratingsdf["score"], (venue_index, user_index)), shape=(M, N))

        venues_name = dict(zip(self.venuedf['venueid'], self.venuedf['name']))
        venue_id = 3
        # find similarity of venue
        similar_ids = self.find_similar_venue(venue_id)
        # display result
        venue_name = venues_name[venue_id]
        print(f"Since you go {venue_name}")
        for i in similar_ids:
            print(venues_name[i])

    def recommend2user(self, targetid, targetvenue):
        N = len(self.ratingsdf['userid'].unique())
        M = len(self.ratingsdf['venueid'].unique())

        # Map Ids to indices
        self.user_mapper = dict(
            zip(np.unique(self.ratingsdf["userid"]), list(range(N))))
        self.venue_mapper = dict(
            zip(np.unique(self.ratingsdf["venueid"]), list(range(M))))

        # Map indices to IDs
        self.user_inv_mapper = dict(
            zip(list(range(N)), np.unique(self.ratingsdf["userid"])))
        self.venue_inv_mapper = dict(
            zip(list(range(M)), np.unique(self.ratingsdf["venueid"])))

        user_index = [self.user_mapper[i] for i in self.ratingsdf['userid']]
        venue_index = [self.venue_mapper[i] for i in self.ratingsdf['venueid']]

        self.X = csr_matrix(
            (self.ratingsdf["score"], (venue_index, user_index)), shape=(M, N))

        # find top rate of user
        target_ratingdf = self.ratingsdf.loc[self.ratingsdf['userid'] == targetid]
        target_ratingdf = target_ratingdf.sort_values(
            by='score', ascending=False)
        target_top_score = target_ratingdf.iat[0, 0]
        # find similarity of venue
        find = []
        for i in range(2, 20):
            find.append(self.find_similar_venue(
                target_top_score, targetvenue, i))

        return find

    """
    Find similar venue using KNN
    """

    def find_similar_venue(self, venue_id, targetvenue, k):

        neighbour_ids = []

        venue_ind = self.venue_mapper[venue_id]
        venue_vec = self.X[venue_ind]

        k += 1
        kNN = NearestNeighbors(
            n_neighbors=k, algorithm="brute", metric=self.metric)
        kNN.fit(self.X)
        venue_vec = venue_vec.reshape(1, -1)
        neighbour = kNN.kneighbors(venue_vec, return_distance=False)
        for i in range(0, k):
            n = neighbour.item(i)
            neighbour_ids.append(self.venue_inv_mapper[n])
        neighbour_ids.pop(0)

        return targetvenue in neighbour_ids
        # return neighbour_ids

# knn = RSKNN(ratingsdf, userdf, venuedf)
# knn.recommend()
