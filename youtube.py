"""
For load youtube.csv
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
from util import Util

import bs4
import pandas as pd
import time
import csv
import os.path
import os
import sys


def scroll_down(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    currentload = 0
    all_comment = soup.find_all(
        'yt-formatted-string', {'class': 'count-text style-scope ytd-comments-header-renderer'})

    if len(all_comment) > 0:
        all_comment = all_comment[0].text
        all_comment = all_comment.split(' ')[0]
        all_comment = all_comment.replace(',', '')
        all_comment = int(all_comment)
    else:
        return

    n = 10
    count = 0
    loaded = 0

    body = driver.find_element(
        By.TAG_NAME, "body")

    while all_comment > loaded:
        # scroll down
        i = 0
        while i < n:
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            i += 1

        data = driver.page_source
        soup = bs4.BeautifulSoup(data, "lxml")
        currentload = soup.find_all('yt-formatted-string',
                                    {'class': 'style-scope ytd-comment-renderer'})
        if loaded == len(currentload):
            count += 1
        else:
            count = 0

        loaded = len(currentload)

        if count == 3:
            break

        n += 0


def main():
    with open('data/youtube.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')
        link = 1
        for row in spamreader:
            youtube_url = row[0]

            options = webdriver.ChromeOptions()
            options.add_experimental_option(
                'excludeSwitches', ['enable-logging'])
            # open chrome
            driver = webdriver.Chrome(options=options)
            driver.get(youtube_url)
            # wait for loadcontent
            time.sleep(5.0)

            # scroll down
            scroll_down(driver)

            data = driver.page_source
            soup = bs4.BeautifulSoup(data, "lxml")
            comment_element = soup.find_all('yt-formatted-string',
                                            {'class': 'style-scope ytd-comment-renderer'})

            # save comment to csv
            name = youtube_url.split('=')[1]
            filepath = 'results/comment_' + name + '.csv'
            # create file if not exist
            if not os.path.exists(filepath):
                # create file
                open(filepath, 'x', newline='', encoding='utf-8')

            # append file
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                spamwriter = csv.writer(
                    csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for comment in comment_element:
                    spamwriter.writerow([comment.text])

            driver.close()


if __name__ == "__main__":
    main()
