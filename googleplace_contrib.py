"""
For load all users database
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

from rsdb import Rsdb

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


def scrollandload(driver, user_id):

    try:
        review_element = driver.find_element(By.CLASS_NAME, 'TiFmlb')
        allreview = int(review_element.text.split()[0].replace(',', ''))
    except NoSuchElementException:
        return False, False, ""
    except ValueError:
        allreview = int(review_element.text.split(' ')[1].replace(',', ''))

    loaded = 0
    count = 0
    scoll = 2
    temp = 0
    while loaded < allreview:

        try:
            iframe = driver.find_element(By.CLASS_NAME, "m6QErb")
            scroll_origin = ScrollOrigin.from_element(iframe)
            ActionChains(driver).scroll_from_origin(
                scroll_origin, 0, 20000 * scoll).perform()
        except TimeoutException as ex:
            print(ex.msg)
            return False, True, ""
        except InvalidArgumentException as ex:
            print(ex.msg)
            return False, True, ""

        data = driver.page_source
        soup = bs4.BeautifulSoup(data, "lxml")
        reviewtitle = soup.find_all('div', {'class': 'd4r55 YJxk2d'})

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

    review_elements = soup.find_all(
        'div', {'class': 'jftiEf fontBodyMedium t2Acle FwTFEc azD0p'})
    for review in review_elements:
        venue_name = review.find_element('div', {'class': 'd4r55 YJxk2d'}).text
        venue_location = review.find_element(
            'div', {'class': 'RfnDt xJVozb'}).text
        review_score = int(review.find_element(
            'span', {'class': 'kvMYJc'})['aria-label'])
        review_time = getTime(review.find_element(
            'span', {'class': 'rsqaWe'}).text)
        review_comment = review.find_element('span', {'class': 'wiI7pd'}).text

        # check venue name
        venue_id = db.is_exist_venue(venue_name)
        if venue_id:
            # add review
            # insert_review(user_id, venue_id, score, time, comment):
            db.insert_review(user_id, venue_id, review_score,
                             review_time, review_comment)
        else:
            # add venue
            # insert_venue(name, score, latitude, longitude, link):
            db.insert_venue(venue_name, 0, 0, 0, "", venue_location)


def isLoaded(name):
    filepath = "results/user/" + name + ".csv"
    if os.path.exists(filepath):
        return True
    return False


def loacFromCSV():
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
                uname = uname.replace(':', '').strip()
            if '/' in uname:
                uname = uname.replace('/', ' ').strip()

            if uname in set(emptyuser['name']):
                continue
            if isLoaded(uname):
                continue

            # open user profile
            chrome_options = Options()
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-logging"])

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(ulink)

            loaded, iserror, df = scrollandload(uid, driver, uid)

            driver.close()


def main():
    db = Rsdb()
    users = db.get_users()
    with alive_bar(len(users), title='Reading user:', dual_line=True) as bar:
        for user in users:
            user_id = user[0]
            user_name = user[1]
            user_link = user[2]
            user_review = user[3]

            # open user profile
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-logging"])

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(user_link)
            # wait for loadcontent
            time.sleep(3.0)
            loaded, iserror, df = scrollandload(driver)

            bar()
    db.close_connection()


if __name__ == "__main__":
    main()
