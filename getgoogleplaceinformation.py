"""

"""
from asyncio import constants
from json import load
from tkinter import X
from warnings import catch_warnings
from numpy import double
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidArgumentException

from alive_progress import alive_bar

import bs4
import pandas as pd
import time
import csv
import os.path
import os

ulink = "https://www.google.com/maps"
# load venue
venuedf = pd.read_csv("data/venue_metadata.csv", sep='|', encoding='utf-8')

categorydf = pd.DataFrame()
badcategorydf = pd.DataFrame()

path_to_file = 'data/categorydf.csv'
if os.path.exists(path_to_file):
    categorydf = pd.read_csv("data/categorydf.csv", sep='|', encoding='utf-8')
path_to_file = 'data/badcategorydf.csv'
if os.path.exists(path_to_file):
    badcategorydf = pd.read_csv("data/badcategorydf.csv", sep='|', encoding='utf-8')


with alive_bar(len(venuedf)) as bar:  
    for i, row in venuedf.iterrows():
        venue_name = row['name']
        venue_id = row['venueid']
        bar()
        if venue_id in categorydf.values :
            continue
        if venue_id in badcategorydf.values :
            continue        
        try:
            # open web
            chrome_options = Options()
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(ulink)

            inputElement = driver.find_element(By.ID, "searchboxinput")
            inputElement.send_keys(venue_name)
            buttonElement = driver.find_element(By.ID, "searchbox-searchbutton")
            buttonElement.click()
            time.sleep(5)
            strCategory = ""
     
            category = driver.find_element(By.CSS_SELECTOR, '.DkEaL.u6ijk')
            strCategory = category.text
        except:
            if len(badcategorydf) > 0:
                badcategorydf.loc[len(badcategorydf.index)] = [venue_id, venue_name]
            else:
                badcategorydf = pd.DataFrame([[venue_id, venue_name]], columns=['venueid', 'name'])
            
            categorydf.to_csv('data/categorydf.csv', sep='|', encoding='utf-8',index=False)
            badcategorydf.to_csv('data/badcategorydf.csv', sep='|', encoding='utf-8',index=False)
 
        driver.close()
        if strCategory == "":
            continue

        if len(categorydf) > 0:
            categorydf.loc[len(categorydf.index)] = [venue_id, venue_name, strCategory]
        else:
            categorydf = pd.DataFrame([[venue_id, venue_name, strCategory]], columns=['venueid','name', 'category'])        
        

categorydf.to_csv('data/categorydf.csv', sep='|', encoding='utf-8',index=False)
badcategorydf.to_csv('data/badcategorydf.csv', sep='|', encoding='utf-8',index=False)