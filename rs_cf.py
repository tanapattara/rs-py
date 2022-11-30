# https://realpython.com/build-recommendation-engine-collaborative-filtering/
from cgi import test
from curses.ascii import islower
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
from surprise import Dataset, Reader, KNNWithMeans
from util import Util, getfile

# load dataframe
# ratingdf -> venueid|userid|score|time|comment
# ratingsdf = pd.read_csv("data/rating.csv", sep='|')
udf = pd.read_csv("data/_user.csv", sep='|')
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
# ratingsdf = pd.read_csv("data/rating_pop.csv", sep='|')
ratingsdf = pd.read_csv("data/rs_rating.csv", sep='|')


def simuv(uid: int, vid: int, rdf, simdf):

    if len(simdf) > 0 and ((uid in simdf['u'].values and vid in simdf['v'].values) or (vid in simdf['u'].values and uid in simdf['v'].values)):
        return simdf

    udf = rdf.loc[rdf['userid'] == uid]
    vdf = rdf.loc[rdf['userid'] == vid]

    # udf = udf.drop(columns=['comment', 'Exist'])
    # vdf = vdf.drop(columns=['comment', 'Exist'])
    # udf.to_csv('data/udf.csv', sep='|', encoding='utf-8', index=False)
    # vdf.to_csv('data/vdf.csv', sep='|', encoding='utf-8', index=False)

    umean = udf['score'].mean()
    vmean = vdf['score'].mean()

    summ = 0
    sum = 0

    um_pow = 0
    vm_pow = 0
    u_pow = 0
    v_pow = 0

    sim_m_value = 0
    sim_value = 0

    mergedf = udf.merge(vdf, how='inner', on='venueid')

    if len(mergedf) > 0:
        for i, row in udf.iterrows():
            u_rating = float(row['score'])
            um_rating = u_rating - umean
            um_pow += pow(um_rating, 2)
            u_pow += pow(u_rating, 2)

            venueid = int(row['venueid'])
            same_score_df = vdf.loc[vdf['venueid'] == venueid]

            if len(same_score_df) == 0:
                continue

            v_rating = 0
            if len(same_score_df) == 1:
                v_rating = float(same_score_df['score'])
            elif len(same_score_df) > 1:
                v_rating = float(same_score_df['score'].mean())

            vm_rating = v_rating - vmean
            sum += u_rating * v_rating
            summ += um_rating * vm_rating

        for i, row in vdf.iterrows():
            v_rating = float(row['score'])
            vm_rating = v_rating - vmean
            vm_pow += pow(vm_rating, 2)
            v_pow += pow(v_rating, 2)

        if um_pow != 0 and vm_pow != 0:
            sim_m_value = summ / (math.sqrt(um_pow) * math.sqrt(vm_pow))

        if u_pow != 0 and v_pow != 0:
            sim_value = sum / (math.sqrt(u_pow) * math.sqrt(v_pow))

    if len(simdf) > 0:
        simdf.loc[len(simdf.index)] = [uid, vid, sim_value, sim_m_value]
    else:
        simdf = pd.DataFrame([[uid, vid, sim_value, sim_m_value]], columns=[
                             'u', 'v', 's', 'sm'])

    return simdf


def add2predict(u, v, score, pscore, pmscore, df, popScore):
    if len(df) > 0:
        df.loc[len(df.index)] = [u, v, score, pscore, pmscore, popScore]
    else:
        df = pd.DataFrame([[u, v, score, pscore, pmscore, popScore]], columns=[
                          'u', 'v', 'real_score', 'predic_cosin_cf', 'predic_pearson_cf', 'popular'])

    df.to_csv('data/predictdf.csv', sep='|', encoding='utf-8', index=False)
    return df


def pred_cf(uid, vid, uvscore, simdf, predictdf):
    # check top similarity
    sim_df = simdf.loc[simdf['u'] == uid]
    # bestsimdf = bestsimdf.sort_values(by=['s'], ascending=False)
    best_sim_m_df = sim_df.loc[sim_df['sm'] > 0.0]
    best_sim_df = sim_df.loc[sim_df['s'] > 0.5]

    zsim = 0
    zscore = 0

    pred_score_u_2_mean_target = 0
    if len(best_sim_m_df) > 0:
        for simindex, simrow in best_sim_m_df.iterrows():
            v_id = int(simrow['v'])
            if v_id == uid:
                continue

            bestsim = float(simrow['sm'])
            train_v_df = traindf.loc[(traindf['userid'] == v_id) & (
                traindf['venueid'] == target_venue_id)]

            if len(train_v_df) == 0:
                continue

            vscore = 1
            if len(train_v_df) == 1:
                vscore = float(train_v_df['score'])
            else:
                vscore = train_v_df.score.sum() / len(train_v_df)

            zsim += bestsim
            zscore += bestsim * vscore
        if zsim != 0:
            pred_score_u_2_mean_target = zscore / zsim

    pred_score_u_2_target = 0
    if len(best_sim_df) > 0:
        for simindex, simrow in best_sim_df.iterrows():
            v_id = int(simrow['v'])
            if v_id == uid:
                continue

            bestsim = float(simrow['s'])
            train_v_df = traindf.loc[(traindf['userid'] == v_id) & (
                traindf['venueid'] == target_venue_id)]

            if len(train_v_df) == 0:
                continue

            vscore = 1
            if len(train_v_df) == 1:
                vscore = float(train_v_df['score'])
            else:
                vscore = train_v_df.score.sum() / len(train_v_df)

            zsim += bestsim
            zscore += bestsim * vscore
        if zsim != 0:
            pred_score_u_2_target = zscore / zsim

    # get popular
    venuedf = pd.read_csv('data/venue_metadata.csv', sep='|')
    row = venuedf.loc[venuedf['venueid'] == vid]
    popScore = -1

    if (len(row) > 0):
        popScore = float(row['score'])

    predictdf = add2predict(
        uid, vid, uvscore, pred_score_u_2_target, pred_score_u_2_mean_target, predictdf, popScore)
    return predictdf


def validate(pdf):
    # u|v|real_score|predic_cosin_cf|predic_pearson_cf|popular
    rmse_sumc = 0
    rmse_sump = 0
    rmse_sumpop = 0
    mae_sumc = 0
    mae_sump = 0
    mae_sumpop = 0
    for index, row in pdf.iterrows():
        r = row.real_score
        p_c = row.predic_cosin_cf
        p_p = row.predic_pearson_cf
        p_pop = row.popular

        # rmse
        rmse_sumc = rmse_sumc + pow((p_c - r), 2)
        rmse_sump = rmse_sump + pow(p_p - r, 2)
        rmse_sumpop = rmse_sumpop + pow(p_pop - r, 2)
        # mae
        mae_sumc = mae_sumc + abs(p_c - r)
        mae_sump = mae_sump + abs(p_p - r)
        mae_sumpop = mae_sumpop + abs(p_pop - r)

    rmse_sumc = math.sqrt(rmse_sumc / len(pdf))
    rmse_sump = math.sqrt(rmse_sump / len(pdf))
    rmse_sumpop = math.sqrt(rmse_sumpop / len(pdf))
    mae_sumc = math.sqrt(mae_sumc / len(pdf))
    mae_sump = math.sqrt(mae_sump / len(pdf))
    mae_sumpop = math.sqrt(mae_sumpop / len(pdf))
    df = pd.DataFrame([[rmse_sumc, rmse_sump, rmse_sumpop, mae_sumc, mae_sump, mae_sumpop]], columns=[
        'rmse_cf_cosin', 'rmse_cf_pearson', 'rmse_pop', 'mae_cf_cosin', 'mae_cf_pearson', 'mae_pop'])
    df.to_csv('data/validate.csv', sep='|')


# train-test data
testdf = pd.DataFrame()
traindf = pd.DataFrame()

filepath = 'data/testdf.csv'
if os.path.exists(filepath):
    testdf = pd.read_csv("data/testdf.csv", sep='|')
    traindf = pd.read_csv("data/traindf.csv", sep='|')
else:
    testdf = ratingsdf.sample(frac=0.1, replace=True, random_state=1)
    traindf = pd.concat([ratingsdf, testdf]).drop_duplicates(keep=False)


testdf.to_csv('data/testdf.csv', sep='|', encoding='utf-8', index=False)
traindf.to_csv('data/traindf.csv', sep='|', encoding='utf-8', index=False)

isLoad = False
simdf = Util.getfile('data/simdf.csv', isLoad)
predictdf = Util.getfile('data/predictdf.csv', isLoad)

testi = 0
for index, row in testdf.iterrows():
    testi += 1
    target_useru_id = int(row['userid'])
    target_venue_id = int(row['venueid'])
    target_score = row['score']

    if len(predictdf) > 0 and (target_useru_id in predictdf['u'].values and target_venue_id in predictdf['v'].values):
        continue

    target_venue_user_rating_df = traindf.loc[traindf['venueid']
                                              == target_venue_id]
    if len(target_venue_user_rating_df) <= 1:
        continue

    # loop all user that rating at target venue
    with alive_bar(len(target_venue_user_rating_df), title=f'working {testi:,}/{len(testdf):,}') as bar:
        for useridex, user_rating_row in target_venue_user_rating_df.iterrows():
            bar()
            user_v_id = int(user_rating_row['userid'])
            if target_useru_id == user_v_id:
                continue

            # venue df that show all usercheckin
            user_v_checkin_df = traindf.loc[traindf['userid'] == user_v_id]
            simdf = simuv(target_useru_id, user_v_id, rdf=traindf, simdf=simdf)
            simdf.to_csv('data/simdf.csv', sep='|',
                         encoding='utf-8', index=False)
    predictdf = pred_cf(target_useru_id, target_venue_id,
                        target_score, simdf, predictdf)
validate(predictdf)
