"""
Read all place.csv in results/csv

return user.csv, venue.csv and rating.csv in data/
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

from alive_progress import alive_bar
from os import listdir
from os.path import isfile, join

def addUser(df, username, link, review):
    key = 1
    path_to_file = "data/user.csv"
    if len(df) > 0:
        # have data in df
        if username not in df.values:           
            # add username data in df 
            key = len(df) + 1  
            newuser = pd.DataFrame([[key, username, link, review]], columns=['userid', 'name', 'link', 'review'])    
            df = pd.concat([df, newuser], ignore_index = True)
        else:
            row = df.loc[df['name'] == username]
            key = int(row['userid'])
    else:
        newuser = pd.DataFrame([[key, username, link, review]], columns=['userid', 'name', 'link', 'review'])  
        df = pd.concat([df, newuser], ignore_index = True)    
    return key, df

def addVenue(df, venueName):
    key = 1
    #remove filetype
    venueName = venueName.split('.')[0]
    link, category = getVenueLink(venueName)
    path_to_file = "data/venue.csv"
    if len(df) > 0:
        # have data in df
        if venueName not in df.values:           
            # add username data in df
            key = len(df) + 1
            newVenue = pd.DataFrame([[key, venueName, category, link]], columns=['venueid', 'name', 'category', 'link'])
            df = pd.concat([df, newVenue], ignore_index = True)
        else:
            row = df.loc[df['name'] == venuename]
            key = int(row['venueid'])        
    else:
        newVenue = pd.DataFrame([[key, venueName, category, link]], columns=['venueid', 'name', 'category', 'link'])
        df = pd.concat([df, newVenue], ignore_index = True) 
    return key, df

def getVenueLink(venueName):
    df = pd.read_csv('results/place.csv', sep='|')
    link = ""
    for index, row in df.iterrows():
        if venueName in row['name']:
            link = row.link
            category = row.category
            break    
    return link, category


mypath = "results/csv/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

userdf = pd.DataFrame()
venuedf = pd.DataFrame()
ratingdf = pd.DataFrame()

i = 1
for venuename in onlyfiles:
    venueid, venuedf = addVenue(venuedf, venuename)

    #load file
    filepath = mypath + venuename
    place = pd.read_csv(filepath, sep="|")
    # loop all place
    titlebar = f'loading venue {i}/{len(onlyfiles)}'
    with alive_bar(len(place), title=titlebar) as bar:        
        for index, row in place.iterrows():
            username = row['name'].strip()      

            score = float(row['score'])
            time = float(row['time'])
            comment = row['comment']
            link = row['link']
            review = row['review']

            userid, userdf = addUser(userdf, username, link, review)  
            #add id to ratingdf name,score,time,comment
            newRating = pd.DataFrame([[venueid, userid, score, time, comment]], columns=['venueid', 'userid', 'score', 'time', 'comment'])
            ratingdf = pd.concat([ratingdf, newRating], ignore_index = True)

            bar()
    i = i+1

ratingdf.to_csv('data/rating.csv', sep='|', encoding='utf-8',index=False)
userdf.to_csv('data/user.csv', sep='|', encoding='utf-8',index=False)
venuedf.to_csv('data/venue.csv', sep='|', encoding='utf-8',index=False)