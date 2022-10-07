# https://realpython.com/build-recommendation-engine-collaborative-filtering/
from cgi import test
import math
from unittest import result
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
from alive_progress import alive_bar
import os.path
import os
from scipy import spatial
from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
from alive_progress import alive_bar

# load dataframe
# ratingdf -> venueid|userid|score|time|comment
# ratingsdf = pd.read_csv("data/rating.csv", sep='|')
udf = pd.read_csv("data/user.csv", sep='|')
# venuedf -> venueid|name|location|vote_count|vote_average|score
# venuedf = pd.read_csv("data/venue.csv", sep='|')
# venuedf_meta -> venueid|name|location|vote_count|vote_average|score
# venuedf = pd.read_csv("data/venue_metadata.csv", sep='|')
# vdf = venuedf[['venueid']]
# remove checkin less out baseon venue_metadata.csv
# df = pd.merge(ratingsdf, vdf, how="left", indicator='Exist')
# df['Exist'] = np.where(df.Exist == 'both', True, False)
# ratingsdf = df[df['Exist']==True].drop(['Exist'], axis=1)
# df.to_csv('data/rating_pop.csv', sep='|', encoding='utf-8',index=False)

# ratingdf -> venueid|userid|score|time|comment
ratingsdf = pd.read_csv("data/rating_pop.csv", sep='|')

def simuv(uid, vid, rdf, simdf):

    if len(simdf) > 0 and ((uid in simdf['u'] and vid in simdf['v']) or (vid in simdf['u'] and uid in simdf['v'])):
        return simdf

    udf = rdf.loc[rdf['userid'] == uid]
    vdf = rdf.loc[rdf['userid'] == vid]
    umean = udf['score'].mean()
    vmean = vdf['score'].mean()
    sum = 0
    upow = 0
    vpow = 0
    for i, row in udf.iterrows():
        venueid = row['venueid']
        urating = row['score'] - umean
        upow += urating * urating
        if len(vdf.loc[vdf['venueid'] == venueid]) != 0:
            vrating = vdf['score'].loc[vdf['venueid'] == venueid].values[0] - vmean
            sum += urating * vrating
    for i, row in vdf.iterrows():
        vrating = row['score'] - umean
        vpow += vrating * vrating
    
    simvalue = sum / math.sqrt(upow) * math.sqrt(vpow)

    if len(simdf) > 0:
        simdf.loc[len(simdf.index)] = [uid, vid, simvalue]
    else:
        simdf = pd.DataFrame([[uid, vid, simvalue]], columns=['u', 'v', 's'])

    return simdf


simdf = pd.DataFrame()
for index, row in ratingsdf.iterrows():
    uid = row['userid']
    # get userdf
    udf = ratingsdf.loc[ratingsdf['userid'] == uid]
    # loop all userdf
    for useridex, urow in udf.iterrows():
        venueid = urow['venueid']
        # venue df that show all usercheckin
        venuedf = ratingsdf.loc[ratingsdf['venueid'] == venueid]
        titlebar = f'loading {index}/{len(ratingsdf)} at user {useridex}/{len(udf)}'
        with alive_bar(len(venuedf), title=titlebar) as bar:  
            for vindex, vrow in venuedf.iterrows():
                vid = vrow['userid']
                if uid == vid:
                    continue
                simdf = simuv(uid, vid, rdf=ratingsdf, simdf=simdf)
                bar()
            

simdf.to_csv('data/simdf.csv', sep='|', encoding='utf-8',index=False)