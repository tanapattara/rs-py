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
from util import Util

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


def scrollandload(driver, db, user_id, titlebar):

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

    # scroll and load all review
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

    # get more button
    more_review_btn_elements = driver.find_elements(
        By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')
    for more_btn in more_review_btn_elements:
        try:
            if more_btn:
                ActionChains(driver).click(more_btn).perform()
        except Exception as e:
            print("no button to click", end='\r')
    # get all review
    review_elements = soup.find_all(
        'div', {'class': 'jftiEf fontBodyMedium t2Acle FwTFEc azD0p'})
    with alive_bar(len(review_elements), title=titlebar, dual_line=True) as bar:
        for review in review_elements:
            venue_name = review.find('div', {'class': 'd4r55 YJxk2d'}).text
            venue_location = review.find(
                'div', {'class': 'RfnDt xJVozb'}).text
            review_score = review.find(
                'span', {'class': 'kvMYJc'})['aria-label']
            review_score = int(review_score.split(' ')[0])
            review_time = getTime(review.find(
                'span', {'class': 'rsqaWe'}).text)
            review_comment = review.find('span', {'class': 'wiI7pd'})
            if review_comment:
                review_comment = review_comment.text
            else:
                review_comment = ""

            venue_province = Util.getProvince(venue_location)

            # check venue name
            venue_id = db.is_exist_venue(venue_name)
            if venue_id:
                # add review
                db.insert_review(user_id, venue_id, review_score,
                                 review_time, review_comment)
            else:
                # add venue
                # insert_venue(self, name, score, latitude, longitude, link, venue_location):
                venue_id = db.insert_venue(
                    venue_name, 0, 0, 0, "", venue_location, venue_province)
                db.insert_review(user_id, venue_id, review_score,
                                 review_time, review_comment)
            bar()


def main():
    db = Rsdb()
    users = db.get_users()
    for user in users:
        user_id = user[0]
        user_name = user[1]
        user_link = user[2]
        user_review = user[3]

        # open user profile
        chrome_options = Options()
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(user_link)
        # wait for loadcontent
        time.sleep(3.0)
        titlebar = f"Loading {user_id} / {len(users)} review"
        scrollandload(driver, db, user_id, titlebar)

    db.close_connection()


if __name__ == "__main__":
    main()
