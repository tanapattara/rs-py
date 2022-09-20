"""

"""
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
with alive_bar(len(venuedf)) as bar:  
    for i, row in venuedf.iterrows():
        venue_name = row['name']
        venue_id = row['venueid']
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
        time.sleep(3)
        try:
            category = driver.find_element(By.CSS_SELECTOR, '.DkEaL.u6ijk')
        except NoSuchElementException:
            # have many place
            # select top list
            listitem = driver.find_element(By.CLASS_NAME, 'hfpxzc')
            listitem.click()
            time.sleep(1)
            # load again
            category = driver.find_element(By.CSS_SELECTOR, '.DkEaL.u6ijk')

        strCategory = category.text

        if len(categorydf) > 0:
            categorydf.loc[len(categorydf.index)] = [venue_id, strCategory]
        else:
            categorydf = pd.DataFrame([[venue_id, strCategory]], columns=['venueid', 'category'])
        driver.close()
        bar()

categorydf.to_csv('data/categorydf.csv', sep='|', encoding='utf-8',index=False)