"""
For load placelist.csv

return result of place.csv in results/csv folder
"""
from tkinter import X
from warnings import catch_warnings
from numpy import double
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from alive_progress import alive_bar

import bs4
import pandas as pd
import time
import csv
import os.path
import os

def scrollandload(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    all_review_score = soup.find_all('div',{'class':'fontBodySmall'})
    allcomment = int(all_review_score[0].text.split()[0].replace(',', ''))
    loaded = 0
    n = 10
    count = 0
    while loaded < allcomment:        
        i = 0

        while i < n:
            html = driver.find_elements(By.CLASS_NAME,'DxyBCb')
            html[0].send_keys(Keys.PAGE_DOWN)    
            i += 1        

        data = driver.page_source
        soup = bs4.BeautifulSoup(data, "lxml")
        currentload = soup.find_all('div',{'class':'jftiEf fontBodyMedium'})
        
        if loaded == len(currentload):
            count += 1
        
        loaded = len(currentload)

        if count == 3:
            break
        
        n += 10            

def convertTime(ttext):

    if "เดือน" in ttext:
        tsplited = ttext.split()
        try:
            tsplited = int(tsplited[0])
        except ValueError:
            tsplited = 1

        if tsplited > 9:
            return double(1)
        else:
            tsplited = tsplited / 10
            return double(tsplited)    
    elif "ปี" in ttext:
        tsplited = ttext.split()
        if len(tsplited) > 1:
            return double(tsplited[0])
        else:
            return 1.0
    else:
        return 0.1

def loaddata(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    all_review_score = soup.find_all('div',{'class':'jftiEf fontBodyMedium'})

    list_name = []
    list_score = []
    list_time = []
    list_comment = []
    list_link = []
    list_review = []

    with alive_bar(len(all_review_score)) as bar:
        for review_element in all_review_score:
            name = review_element['aria-label']

            user_link = review_element.findChildren('a', {'class':'WEBjve'})[0]['href']
            
            user_review = review_element.findChildren('div', {'class':'RfnDt'})

            user_review_n = 0

            if len(user_review) > 0:
                user_review = review_element.findChildren('div', {'class':'RfnDt'})[0]

                txt = ''
                try:            
                    if len(list(user_review.children)) == 1:
                        txt = list(user_review.children)[0].text
                    elif len(list(user_review.children)) == 2:
                        txt = list(user_review.children)[1].text

                    if '·' in txt:
                        txt = txt.replace('·', '').strip()
                    if bool(txt.strip()):
                        txt = txt.split(' ')[0]
                        if ',' in txt:
                            txt = txt.replace(',','').strip()
                        user_review_n = int(txt)
                except:
                    print(txt)
            
            profiles = review_element.findChildren('div', {'class':'DU9Pgb'})
            pf = list(profiles)[0]
            score = pf.findChildren('span', {'class':'kvMYJc'})[0]
            score = score['aria-label'].split()[0]
            stime = pf.findChildren('span', {'class':'rsqaWe'})[0]
            stime = convertTime(stime.text)
            comment = review_element.findChildren('span', {'class':'wiI7pd'})
            comment = comment[0].text

            list_name.append(name)
            list_score.append(score)
            list_time.append(stime)
            list_comment.append(comment)
            list_link.append(user_link)
            list_review.append(user_review_n)
            bar()
            

    df = pd.DataFrame([list_name, list_score, list_time, list_comment, list_link, list_review])
    df = df.transpose()
    df.columns = ['name', 'score', 'time', 'comment', 'link', 'review']
    return df

def saveplacedetail(driver, lat, lon, place_url):
    #get name of place
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    name_element = soup.find_all('h1',{'class':'DUwDvf fontHeadlineLarge'})
    place_name = name_element[0].text.strip()
    #get overall score of place
    p_score = soup.find_all('div', {'class', 'F7nice mmu3tf'})

    place_score = 0
    try:
        if(p_score[0].span.text.strip() != ''):
            place_score = float(p_score[0].span.text)
    except:
        place_score = 0
            

    #get category
    place_detail = soup.find_all('div', {'class', 'skqShb'})
    place_category = place_detail[0].contents[1].text.replace('·','') if '·' in  place_detail[0].contents[1].text else place_detail[0].contents[1].text
    
    #add place data to dataframe
    place_data_df = pd.DataFrame([place_name, place_score, place_category, lat, lon, place_url])
    place_data_df = place_data_df.transpose()
    place_data_df.columns = ['name','score','category','latitude','longitude', 'link']
    path_to_file = 'results\place.csv'
    
    parent_dir = ""
    dirxlsx= "results"
    path = os.path.join(parent_dir, dirxlsx)
    try:
        if not os.path.exists(path):
            os.makedirs(path, 0o666)
    except OSError:
        print('Fatal: output directory "' + path + '" does not exist and cannot be created')

    #check exist data in place.csv file
    isExistRecord = False
    if os.path.exists(path_to_file):
        existdata = pd.read_csv(path_to_file, sep='|')
        for index, row in existdata.iterrows():
            if place_name in row['name']:
                isExistRecord = True
                print(place_name + " is already exist.")
                break
        if not isExistRecord:
            place_data_df = pd.concat([existdata, place_data_df], ignore_index = True) 

    return [isExistRecord, place_name, place_data_df]

def loadPlacelist():
    with open('data/placelist.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')

        for row in spamreader:      
            place_url = row[0]

            #find location
            surl = place_url.split('/')
            locations = [x for x in surl if "@" in x]
            if len(locations) > 1:
                i = 0
                for loc in locations:
                    if len(loc.split(',')) == 3:
                        break
                    i += 1
                locations = locations[i]
            else:
                locations = locations[0]

            lat = float(locations.split(',')[0].replace('@',''))
            lon = float(locations.split(',')[1])

            #open chrome
            driver = webdriver.Chrome()
            driver.get(place_url)

            # wait for loadcontent
            time.sleep(3.0)
    
            existrecord, place_name, place_data_df = saveplacedetail(driver, lat, lon, place_url)

            if existrecord:
                driver.close()
                continue

            #get review button
            review_buttons = driver.find_elements(By.CLASS_NAME, 'HHrUdb')
            if len(review_buttons) > 0:
                last_element = review_buttons[-1]
                ActionChains(driver).click(last_element).perform()
                time.sleep(3.0)
                scrollandload(driver)
                data_loaded = loaddata(driver)

                parent_dir = "results"

                dircsv = "csv"       

                #save to csv
                path = os.path.join(parent_dir, dircsv)
                try:
                    if not os.path.exists(path):
                        os.makedirs(path, 0o666)
                except OSError:
                    print('Fatal: output directory "' + path + '" does not exist and cannot be created')
                data_loaded.to_csv('results/csv/' + place_name + '.csv', index=False, encoding='utf-8', sep='|')

                place_data_df.to_csv('results/place.csv', index=False, encoding='utf-8', sep='|')    
            else:
                print('can\'t find review button')            
                continue

            driver.close()