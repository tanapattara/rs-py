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
from rsdb import Rsdb

import bs4
import pandas as pd
import time
import csv
import os.path
import os
import sys


def scrollandload(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    all_review_score = soup.find('div', {'class': 'fontBodySmall'})
    try:
        allcomment = int(all_review_score.text.split()[0].replace(',', ''))
    except ValueError:
        allcomment = 1000
    loaded = 0
    n = 10
    count = 0
    while loaded < allcomment:
        i = 0

        while i < n:
            html = driver.find_elements(By.CLASS_NAME, 'DxyBCb')
            html[0].send_keys(Keys.PAGE_DOWN)
            i += 1

        data = driver.page_source
        soup = bs4.BeautifulSoup(data, "lxml")
        currentload = soup.find_all('div', {'class': 'jftiEf fontBodyMedium'})

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
            return float(1)
        else:
            tsplited = tsplited / 10
            return float(tsplited)
    elif "ปี" in ttext:
        tsplited = ttext.split()
        if len(tsplited) > 1:
            return float(tsplited[0])
        else:
            return float(1.0)
    else:
        return float(0.1)


def loaddata(driver, db, place_name, place_category, place_score, lat, lon, place_url, place_location, titlenbar):

    # get more review button
    more_review_btn_elements = driver.find_elements(
        By.CSS_SELECTOR, "div.MyEned")
    for more_btn in more_review_btn_elements:
        try:
            more_review_btn_element = more_btn.find_element(
                By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
            if more_review_btn_element:
                ActionChains(driver).click(more_review_btn_element).perform()
        except Exception as e:
            print("no button to click", end='\r')

    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    all_review_score = soup.find_all('div', {'class': 'jftiEf fontBodyMedium'})

    # insert data to database
    db_category_id = db.insert_category(place_category)
    db_venue_id = db.insert_venue(
        place_name, place_score, lat, lon, place_url, place_location)
    db.insert_venue_category(db_venue_id, db_category_id)

    with alive_bar(len(all_review_score), title=titlenbar) as bar:
        for review_element in all_review_score:

            name = review_element['aria-label']

            user_link = review_element.find(
                'button', {'class': 'al6Kxe'}).get('data-href')

            user_review_n = 0
            user_review = review_element.find(
                'div', {'class': 'RfnDt'})
            if user_review:
                txt = user_review.text
                try:
                    # check if user review is number
                    if 'รีวิว' in txt:
                        txt = txt.replace('รีวิว', '').strip()
                    if '·' in txt:
                        txt = txt.replace('·', '').strip()
                    if 'Local Guide' in txt:
                        txt = txt.replace('Local Guide', '').strip()
                    if ',' in txt:
                        txt = txt.replace(',', '').strip()
                    user_review_n = int(txt)
                except:
                    user_review_n = 0

            score = review_element.find('span', {'class': 'kvMYJc'})
            score = int(score['aria-label'].split()[0])

            stime = review_element.find('span', {'class': 'rsqaWe'}).text
            stime = convertTime(stime)

            # get comment
            comment = ""
            comment_element = review_element.find('span', {'class': 'wiI7pd'})
            if comment_element:
                comment = comment_element.text

            # save to db
            user_id = db.insert_user(name, user_link, user_review_n)
            review_id = db.insert_review(
                user_id, db_venue_id, score, stime, comment)

            bar()


def get_and_check_venue(driver, db):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    name_element = soup.find('h1', {'class': 'DUwDvf fontHeadlineLarge'})
    place_name = name_element.text.strip()

    db_venue_id = db.is_exist_venue(place_name)
    isExistRecord = False
    if db_venue_id:
        isExistRecord = True
        place_category = db.get_venue_category(db_venue_id)
        place = db.get_venue_data(db_venue_id)
        place_score = place[2]
        place_location = place[5]
    else:
        p_score = soup.find('span', {'class', 'ceNzKf'})
        if p_score:
            place_score = float(p_score['aria-label'].split()[0])
        else:
            place_score = 0
        # get category
        place_detail = soup.find_all('div', {'class', 'skqShb'})
        place_category = place_detail[0].contents[1].text.replace(
            '·', '') if '·' in place_detail[0].contents[1].text else place_detail[0].contents[1].text
        place_location = soup.find(
            'div', {'class': 'Io6YTe fontBodyMedium kR99db'})
        if place_location:
            place_location = place_location.text
        else:
            place_location = ""

    return [isExistRecord, db_venue_id, place_name, place_category, place_score, place_location]


def saveplacedetail(driver, lat, lon, place_url, place_location, db):
    # get name of place
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    name_element = soup.find('h1', {'class': 'DUwDvf fontHeadlineLarge'})
    place_name = name_element.text.strip()

    # check if place is exist in database
    db_venue_id = db.is_exist_venue(place_name)
    isExistRecord = False
    if db_venue_id:
        isExistRecord = True

    if not isExistRecord or isForceUpdate:
        # get overall score of place
        p_score = soup.find('span', {'class', 'ceNzKf'})
        if p_score:
            place_score = float(p_score['aria-label'].split()[0])
        else:
            place_score = 0

        # get category
        place_detail = soup.find_all('div', {'class', 'skqShb'})
        place_category = place_detail[0].contents[1].text.replace(
            '·', '') if '·' in place_detail[0].contents[1].text else place_detail[0].contents[1].text
        # add place data to dataframe
        place_data_df = pd.DataFrame(
            [place_name, place_score, place_category, lat, lon, place_url])
        place_data_df = place_data_df.transpose()
        place_data_df.columns = ['name', 'score',
                                 'category', 'latitude', 'longitude', 'link']

        # insert data to database
        db_category_id = db.insert_category(place_category)
        db_venue_id = db.insert_venue(
            place_name, place_score, lat, lon, place_url, place_location)
        db.insert_venue_category(db_venue_id, db_category_id)

    return [isExistRecord, place_name, db_venue_id]


def loadfromfile(db):
    with open('data/placelist.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')
        iplace = 1
        for row in spamreader:
            place_url = row[0]

            dbexist = db.is_exist_venue_url(place_url)
            if dbexist and not isForceUpdate:
                iplace += 1
                continue

            # find location
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

            lat = float(locations.split(',')[0].replace('@', ''))
            lon = float(locations.split(',')[1])

            options = webdriver.ChromeOptions()
            options.add_experimental_option(
                'excludeSwitches', ['enable-logging'])

            # open chrome
            driver = webdriver.Chrome(
                options=options)
            driver.get(place_url)

            # wait for loadcontent
            time.sleep(3.0)

            # check exist record
            existrecord, venue_id, place_name, place_category, place_score, place_location = get_and_check_venue(
                driver, db)

            # check exist data in place.csv file
            if existrecord and not isForceUpdate:
                driver.close()
                continue

            # get review button
            review_buttons = driver.find_elements(By.CLASS_NAME, 'HHrUdb')
            if len(review_buttons) > 0:
                last_element = review_buttons[-1]
                ActionChains(driver).click(last_element).perform()
                time.sleep(3.0)
                scrollandload(driver)
                titlenbar = "Place " + str(iplace) + " : " + place_name + " : "
                loaddata(driver, db, place_name, place_category,
                         place_score, lat, lon, place_url, place_location, titlenbar)
            else:
                print('can\'t find review button')
                continue

            driver.close()
            iplace += 1


def main():
    global isForceUpdate
    isForceUpdate = False
    if len(sys.argv) > 1:
        # loop all argv
        args = len(sys.argv) - 1
        pos = 1
        while (args >= pos):
            if sys.argv[pos] == '--empty-db':
                db = Rsdb()
                db.drop_all_table()
                db.close_connection()
            if sys.argv[pos] == '--force-update':
                isForceUpdate = True
            pos += 1

    db = Rsdb()
    loadfromfile(db)
    db.close_connection()


if __name__ == "__main__":
    main()
