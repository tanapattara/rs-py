"""
Read all user file in result/user

return result user.csv, venue.csv and rating.csv
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

def remove_empty_review():
    # read empty record 
    emptydf = pd.read_csv('data/emptyuser.csv', sep="|", encoding='utf-8')
    emptydf = emptydf.drop(columns=['name','link','msg'])
    # read user.csv
    userdf = pd.read_csv('data/user.csv', sep="|", encoding='utf-8')
    # remove empty rating from user.csv
    diff = userdf.merge(emptydf, indicator = True, how='left').loc[lambda x : x['_merge']!='both']
    diff = diff.drop(columns=['_merge'])
    diff.to_csv('data/user2.csv', sep='|', encoding='utf-8',index=False)

def addVenue(df, venueName, vanue_location):
    key = 1
    path_to_file = "data/venue.csv"
    if len(df) > 0:
        # have data in df
        if venueName not in df.name.values:           
            # add username data in df
            key = len(df) + 1
            newVenue = pd.DataFrame([[key, venueName, vanue_location]], columns=['venueid', 'name', 'location'])
            df = pd.concat([df, newVenue], ignore_index = True)
        else:
            row = df.loc[df.name == venueName]   
            if len(row) == 1:    
                key = row.iloc[0]['venueid']
            else:
                print("Multi venue name")
    else:
        newVenue = pd.DataFrame([[key, venueName, vanue_location]], columns=['venueid', 'name', 'location'])
        df = pd.concat([df, newVenue], ignore_index = True) 
    return key, df

def create_raw_data():
    venuedf = pd.DataFrame()
    ratingdf = pd.DataFrame()

    mypath = "results/user/"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    i = 1
    for username in onlyfiles:
        filepath = mypath + username
        review_from_user = pd.read_csv(filepath, sep="|")
        titlebar = f'loading user {i}/{len(onlyfiles)}'
        with alive_bar(len(review_from_user), title=titlebar) as bar:        
            for index, row in review_from_user.iterrows():
                userid = row['userid']
                venue_name = row['venue_name']
                venue_location = row['vanue_location']
                score = row['score']
                time = row['time']
                comment = row['comment']

                venueid, venuedf = addVenue(venuedf, venue_name, venue_location)
                newRating = pd.DataFrame([[venueid, userid, score, time, comment]], columns=['venueid', 'userid', 'score', 'time', 'comment'])
                ratingdf = pd.concat([ratingdf, newRating], ignore_index = True)
                bar()
        i = i+1

    ratingdf.to_csv('data/rating.csv', sep='|', encoding='utf-8',index=False)
    venuedf.to_csv('data/venue.csv', sep='|', encoding='utf-8',index=False)

    
# remove_empty_review()
create_raw_data()