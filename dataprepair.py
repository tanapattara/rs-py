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

def addUser(df, username):
    key = 1
    path_to_file = "data/user.csv"
    if len(df) > 0:
        # have data in df
        if username not in df.values:           
            # add username data in df 
            key = len(df) + 1  
            newuser = pd.DataFrame([[key, username]], columns=['userid', 'name'])    
            df = pd.concat([df, newuser], ignore_index = True)
    else:
        newuser = pd.DataFrame([[key, username]], columns=['userid', 'name'])
        # no data in df
        if os.path.exists(path_to_file):
            # load file
            df = pd.read_csv(path_to_file)   
        df = pd.concat([df, newuser], ignore_index = True)    
    return [key, df]

def addVenue(df, venueName):
    key = 1
    #remove filetype
    venueName = venueName.split('.')[0]
    path_to_file = "data/venue.csv"
    if len(df) > 0:
        # have data in df
        if venueName not in df.values:           
            # add username data in df
            key = len(df) + 1
            newVenue = pd.DataFrame([[key, venueName]], columns=['venueid', 'name'])
            df = pd.concat([df, newVenue], ignore_index = True)
        
    else:
        newVenue = pd.DataFrame([[key, venueName]], columns=['venueid', 'name'])
        # no data in df
        if os.path.exists(path_to_file):
            # load file
            df = pd.read_csv(path_to_file)   
        df = pd.concat([df, newVenue], ignore_index = True) 
    return [key, df]

mypath = "results/csv/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

userdf = pd.DataFrame()
venuedf = pd.DataFrame()
ratingdf = pd.DataFrame()

for venuename in onlyfiles:
    _venue = addVenue(venuedf, venuename)
    venueid = _venue[0]
    venuedf = _venue[1]

    #load file
    filepath = mypath + venuename
    place = pd.read_csv(filepath)
    # loop all place
    with alive_bar(len(place)) as bar:        
        for index, row in place.iterrows():
            username = row['name'].strip()
            _user = addUser(userdf, username)
            userid = _user[0]
            userdf = _user[1]            

            score = float(row['score'])
            time = float(row['time'])
            comment = row['comment']
            #add id to ratingdf name,score,time,comment
            newRating = pd.DataFrame([[venueid, userid, score, time, comment]], columns=['venueid', 'userid', 'score', 'time', 'comment'])
            ratingdf = pd.concat([ratingdf, newRating], ignore_index = True)

            bar()

ratingdf.to_csv('data/rating.csv', sep='\t', encoding='utf-8')
userdf.to_csv('data/user.csv', sep='\t', encoding='utf-8')
venuedf.to_csv('data/venue.csv', sep='\t', encoding='utf-8')