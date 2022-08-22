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

def getTime(timetext):
    
    if "สัปดาห์" in timetext or "วัน" in timetext:
        return 0.1

    if "เดือน" in timetext:
        txt = timetext.split(' ')
        if len(txt) > 1:
            month = int(txt[0])
            if month > 9:
                return 1.0
            else:
                return month / 10
        else:
            return 0.1
            
    if "ปี" in timetext:
        txt = timetext.split(' ')
        if len(txt) > 1:
            year = int(txt[0])
            return year
        else:
            return 1
    
    return 0.1

def scrollandload(uid, driver): 

    try:
        review_element = driver.find_element(By.CLASS_NAME, 'TiFmlb')
        allreview = int(review_element.text.split()[0].replace(',',''))
    except NoSuchElementException:
        return False, False, ""
    except ValueError:
        allreview = int(review_element.text.split(' ')[1].replace(',',''))


    loaded = 0
    count = 0
    scoll = 2
    temp = 0
    while loaded < allreview:

        try:
            iframe = driver.find_element(By.CLASS_NAME, "m6QErb")
            scroll_origin = ScrollOrigin.from_element(iframe)
            ActionChains(driver).scroll_from_origin(scroll_origin, 0, 20000 * scoll).perform()
        except TimeoutException as ex:
            print(ex.msg)
            return False, True, ""
        except InvalidArgumentException as ex:
            print(ex.msg)
            return False, True, ""
        
        data = driver.page_source
        soup = bs4.BeautifulSoup(data, "lxml")
        reviewtitle = soup.find_all('div',{'class':'d4r55 YJxk2d'})

        loaded = int(len(reviewtitle))
        
        time.sleep(3)      
        scoll += 2

        if temp != loaded:
            temp = loaded            
            count = 0
        elif temp == loaded:
            count += 1

        # print(temp, loaded, count)
        if count == 10:
            break
    
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    
    title = []
    location = []
    score = []
    times = []
    comment = []
    uids = []
    
    element = soup.find_all('div',{'class':'d4r55 YJxk2d'})
    for row in element:
        title.append(row.text.strip())
        uids.append(uid)
    element = soup.find_all('div',{'class':'RfnDt xJVozb'})
    for row in element:
        location.append(row.text.replace('-','').strip())
    element = soup.find_all('span',{'class':'kvMYJc'})
    for row in element:
        s = int(row['aria-label'].replace('ดาว','').strip())
        score.append(s)
    element = soup.find_all('span',{'class':'wiI7pd'})
    for row in element:
        comment.append(row.next)
    element = soup.find_all('span',{'class':'rsqaWe'})
    for row in element:
        timevalue = getTime(row.next)
        times.append(timevalue)

    
    df = pd.DataFrame(list(zip(uids,title, location, score, times, comment)),columns=['userid','venue_name','vanue_location','score','time','comment'])
    return True, False, df

def isLoaded(name):
    filepath = "results/user/" + name + ".csv"
    if os.path.exists(filepath):
        return True
    return False;


# load df from user
userdf = pd.read_csv("data/user.csv", sep='|', encoding='utf-8')
emptyuser = pd.read_csv('data/emptyuser.csv', sep='|', encoding='utf-8')
with alive_bar(len(userdf.index), title='Reading user:', dual_line=True) as bar:
    for i, row in userdf.iterrows():

        ulink = row['link']
        uid = row['userid']
        uname = row['name']
        bar()
        if ":" in uname:
            uname = uname.replace(':','').strip()
        if '/' in uname:
            uname = uname.replace('/',' ').strip()

        if uname in set(emptyuser['name']):
            continue
        if isLoaded(uname):
            continue

        #open user profile
        chrome_options = Options()
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(ulink)

        loaded, iserror, df = scrollandload(uid, driver)
        if loaded:
            df.to_csv('results/user/' + uname + '.csv', index=False, encoding='utf-8', sep='|')
        else:
            #new data
            msg = "nocomment"
            if iserror:
                msg = "error"

            newdata = pd.DataFrame([uid, uname, ulink,msg])
            newdata = newdata.transpose()
            newdata.columns = ['userid','name','link', 'msg']

            # empty user
            path_to_file = 'data\emptyuser.csv'
            if os.path.exists(path_to_file):
                existdata = pd.read_csv(path_to_file, sep='|', encoding='utf-8')
                newdata = pd.concat([existdata, newdata], ignore_index = True) 
            
            newdata.to_csv(path_to_file, index=False, encoding='utf-8', sep='|')

        driver.close()