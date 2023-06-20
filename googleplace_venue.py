"""
For update venue details
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


def main():
    db = Rsdb()

    venues = db.get_empty_venues()
    base_url = "https://www.google.co.th/maps/search/"
    titlebar = "Get venue details"
    with alive_bar(len(venues), title=titlebar, dual_line=True) as bar:
        for venue in venues:
            venue_id = venue[0]
            venue_name = venue[1]

            titlebar = "Update venue : " + \
                str(venue_id) + " of " + str(len(venues))

            chrome_options = Options()
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-logging"])

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(base_url + venue_name)
            time.sleep(3.0)

            data = driver.page_source
            soup = bs4.BeautifulSoup(data, "lxml")

            # check search results
            search_results = soup.find_all(
                'div', {'class': 'Nv2PK Q2HXcd THOPZb'})
            if len(search_results) > 0:
                continue

            venue_score = soup.find('span', {'class': 'ceNzKf'})
            venue_score = Util.convertStar(
                venue_score['aria-label']) if venue_score else 0.0

            venue_category = soup.find('button', {'class': 'DkEaL'})
            venue_category = venue_category.text if venue_category else None

            venue_location = soup.find(
                'div', {'class': 'Io6YTe fontBodyMedium kR99db'})
            venue_location = venue_location.text if venue_location else None

            venue_province = Util.getProvince(venue_location)

            # get current url
            url = driver.current_url
            surl = url.split('/')
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
            if venue_category != None and venue_category.strip() != "":
                # update category
                venue_category_id = db.insert_category(venue_category)
                # update venue
                db.insert_venue_category(venue_id, venue_category_id)

            if "search" in url:
                url = None

            venue_id = db.insert_venue(venue_name, venue_score, lat,
                                       lon, url, venue_location, venue_province)
            if venue_id:
                print("Update venue: " + venue_name)
            bar()
            driver.close()
    db.close_connection()


if __name__ == "__main__":
    main()
