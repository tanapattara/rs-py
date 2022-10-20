# https://realpython.com/build-recommendation-engine-collaborative-filtering/
from cgi import test
import math
from tokenize import Double
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

def simuv(uid:int, vid:int, rdf, simdf):

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
    
    simvalue = 0
    if  upow != 0 and vpow != 0:
        simvalue = sum / math.sqrt(upow) * math.sqrt(vpow)

    if len(simdf) > 0:
        simdf.loc[len(simdf.index)] = [uid, vid, simvalue]
    else:
        simdf = pd.DataFrame([[uid, vid, simvalue]], columns=['u', 'v', 's'])

    return simdf

def getfile(filepath):
    df = pd.DataFrame()
    try:
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, sep='|')
    except:
        return df
    return df

def add2predict(u,v,score, pscore,df):
    if len(df) > 0:
        df.loc[len(df.index)] = [u, v, score, pscore]
        df.to_csv('data/predictdf.csv', sep='|', encoding='utf-8',index=False)
    else:
        df = pd.DataFrame([[u, v, score, pscore]], columns=['u', 'v', 's','p'])

    return df

def pred_cf(uid, vid, uvscore, simdf, predictdf):
    # check top similarity
    bestsimdf = simdf.loc[simdf['u'] == uid]
    bestsimdf = bestsimdf.sort_values(by=['s'], ascending=False)
    bestsimdf = bestsimdf.loc[bestsimdf['s'] > 0.5]
    
    zsim = 0
    zscore = 0
    pred_score_u_2_target = -1
    if len(bestsimdf) > 0:
        for simindex, simrow in bestsimdf.iterrows():
            v_id = int(simrow['v'])
            if v_id == uid:
                continue

            bestsim = int(simrow['s'])
            train_v_df = traindf.loc[(traindf['userid'] == v_id) & (traindf['venueid'] == target_venue_id)]

            if len(train_v_df) == 0:
                continue

            zsim += bestsim
            zscore += bestsim * int(train_v_df['score'])
        if zsim != 0:
            pred_score_u_2_target = zscore / zsim
    
    predictdf = add2predict(uid, vid, uvscore, pred_score_u_2_target, predictdf)
    return predictdf

# train-test data
testdf = pd.DataFrame()
traindf = pd.DataFrame()

filepath = 'data/testdf.csv'
if os.path.exists(filepath):
    testdf = pd.read_csv("data/testdf.csv", sep='|')
    traindf = pd.read_csv("data/traindf.csv", sep='|')
else:
    testdf = ratingsdf.sample(frac=0.1, replace=True, random_state=1)
    traindf = pd.concat([ratingsdf,testdf]).drop_duplicates(keep=False)    

predictdf = getfile('data/predictdf.csv')

testdf.to_csv('data/testdf.csv', sep='|', encoding='utf-8',index=False)
traindf.to_csv('data/traindf.csv', sep='|', encoding='utf-8',index=False)

simdf = getfile('data/simdf.csv')

testi = 0
for index, row in testdf.iterrows():
    target_useru_id = int(row['userid'])
    target_venue_id = int(row['venueid'])
    target_score = row['score']

    if len(predictdf) > 0 and ( target_useru_id in predictdf['u'] and target_venue_id in predictdf['v']):
        continue

    target_venue_user_rating_df = traindf.loc[traindf['venueid'] == target_venue_id]
    if len(target_venue_user_rating_df) <= 1:
        continue

    # loop all user that rating at target venue
    with alive_bar(len(target_venue_user_rating_df), title=f'working {testi}/{len(testdf)}') as bar:
        for useridex, user_rating_row in target_venue_user_rating_df.iterrows():
            bar()
            user_v_id = int(user_rating_row['userid'])
            if target_useru_id == user_v_id:
                continue
            
            # venue df that show all usercheckin
            user_v_checkin_df = traindf.loc[traindf['userid'] == user_v_id]
            simdf = simuv(target_useru_id, user_v_id, rdf=testdf, simdf=simdf)
            simdf.to_csv('data/simdf.csv', sep='|', encoding='utf-8',index=False)
    predictdf = pred_cf(target_useru_id, target_venue_id, target_score, simdf, predictdf)
    testi += 1

