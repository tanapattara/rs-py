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
    all_review_score = soup.find_all('div', {'class': 'fontBodySmall'})
    allcomment = int(all_review_score[0].text.split()[0].replace(',', ''))
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


def loaddata(driver, venue_id, db):

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

    list_name = []
    list_score = []
    list_time = []
    list_comment = []
    list_link = []
    list_review = []

    with alive_bar(len(all_review_score)) as bar:
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
                    user_review_n = int(txt)
                except:
                    print(txt)

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
                user_id, venue_id, score, stime, comment)

            list_name.append(name)
            list_score.append(score)
            list_time.append(stime)
            list_comment.append(comment)
            list_link.append(user_link)
            list_review.append(user_review_n)
            bar()

    df = pd.DataFrame([list_name, list_score, list_time,
                      list_comment, list_link, list_review])
    df = df.transpose()
    df.columns = ['name', 'score', 'time', 'comment', 'link', 'review']
    return df


def saveplacedetail(driver, lat, lon, place_url, db):
    global isSaveCsv
    # get name of place
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    name_element = soup.find_all('h1', {'class': 'DUwDvf fontHeadlineLarge'})
    place_name = name_element[0].text.strip()
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
    isExistRecord = False

    # add place data to dataframe
    place_data_df = pd.DataFrame(
        [place_name, place_score, place_category, lat, lon, place_url])
    place_data_df = place_data_df.transpose()
    place_data_df.columns = ['name', 'score',
                             'category', 'latitude', 'longitude', 'link']

    parent_dir = ""
    dirxlsx = "results"
    path = os.path.join(parent_dir, dirxlsx)
    try:
        if not os.path.exists(path):
            os.makedirs(path, 0o666)
    except OSError:
        print('Fatal: output directory "' + path +
              '" does not exist and cannot be created')

    # check exist data in place.csv file
    path_to_file = 'results\place.csv'
    isExistRecord = False
    if os.path.exists(path_to_file):
        existdata = pd.read_csv(path_to_file, sep='|')
        for index, row in existdata.iterrows():
            if place_name in row['name']:
                isExistRecord = True
                print(place_name + " is already exist.")
                break
        if not isExistRecord:
            place_data_df = pd.concat(
                [existdata, place_data_df], ignore_index=True)

    # save data to db
    isExistVenueInDB = db.is_exist_venue(place_name)
    # insert data to database
    db_category_id = db.insert_category(place_category)
    db_venue_id = db.insert_venue(place_name, place_score, lat, lon, place_url)
    db.insert_venue_category(db_venue_id, db_category_id)

    return [isExistRecord, place_name, place_data_df, db_venue_id]


def loadfromfile(db):
    global isSaveCsv
    with open('data/placelist.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')

        for row in spamreader:
            place_url = row[0]

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

            # open chrome
            driver = webdriver.Chrome()
            driver.get(place_url)

            # wait for loadcontent
            time.sleep(3.0)

            existrecord, place_name, place_data_df, venue_id = saveplacedetail(
                driver, lat, lon, place_url, db)

            # check exist data in place.csv file
            if not isForceUpdate and existrecord:
                driver.close()
                continue

            # get review button
            review_buttons = driver.find_elements(By.CLASS_NAME, 'HHrUdb')
            if len(review_buttons) > 0:
                last_element = review_buttons[-1]
                ActionChains(driver).click(last_element).perform()
                time.sleep(3.0)
                scrollandload(driver)
                data_loaded = loaddata(driver, venue_id, db)

                parent_dir = "results"
                dircsv = "csv"
                if isSaveCsv:
                    # save to csv
                    path = os.path.join(parent_dir, dircsv)
                    try:
                        if not os.path.exists(path):
                            os.makedirs(path, 0o666)
                    except OSError:
                        print('Fatal: output directory "' + path +
                              '" does not exist and cannot be created')
                    data_loaded.to_csv('results/csv/' + place_name +
                                       '.csv', index=False, encoding='utf-8', sep='|')
                    place_data_df.to_csv('results/place.csv',
                                         index=False, encoding='utf-8', sep='|')
            else:
                print('can\'t find review button')
                continue

            driver.close()


def main():
    global isSaveCsv
    global isForceUpdate

    isSaveCsv = False
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
            if sys.argv[pos] == '--csv':
                isSaveCsv = True
            if sys.argv[pos] == '--force-update':
                isForceUpdate = True
            pos += 1

    db = Rsdb()
    loadfromfile(db)
    db.close_connection()


if __name__ == "__main__":
    main()
